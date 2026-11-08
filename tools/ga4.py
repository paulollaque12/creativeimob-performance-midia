#!/usr/bin/env python3
"""GA4 dos sites das imobiliárias → dados/ga4.json (lido por tools/montar.py, marcador /*__GA4__*/null).

Fonte: conector Google Analytics (run_report). Para cada site, CINCO consultas de 2026-01-01 até ONTEM,
cada resposta salva em <pasta>/<chave>_<consulta>.json (as respostas grandes o conector já grava em arquivo):

  cube  date × sessionDefaultChannelGroup × sessionSourceMedium × sessionCampaignName × deviceCategory
        → sessions, engagedSessions, newUsers, screenPageViews, userEngagementDuration
  lp    date × landingPage → sessions, engagedSessions, newUsers   (só linhas com sessions ≥ 3 no dia;
        o resto entra no painel como "demais páginas" = cube − lp)
  ev    date × eventName → eventCount, keyEvents
  utm   date × sessionSource × sessionMedium × sessionCampaignName × sessionManualAdContent (utm_source, utm_medium,
        utm_campaign, utm_content) → sessions, engagedSessions, newUsers, userEngagementDuration
  ct    date × eventName × canal × origem/mídia × campanha × dispositivo × landingPage × utm_content → eventCount,
        filtrado pelos eventos de contato do site (regex em SITES[k]["ct"])

`python3 tools/ga4.py --consultas` imprime os pedidos exatos (JSON) para copiar nas chamadas do conector.
`python3 tools/ga4.py --pasta /tmp/ga [--ate AAAA-MM-DD]` monta dados/ga4.json.
Sem --ate não falha por atraso: GA4 parado vira aviso no painel (ex.: Nova SP sem coleta desde 16/10/2026).
"""
import argparse, datetime as dt, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = dt.date(2024, 1, 1)

# propriedades no doc do projeto claude/mcp_ga4.md (Nova SP 300839307 e Lopes Prime 349413276 também existem)
SITES = {
    # só o site da Taylor (decisão do Paulo em 08/11/2026: GA4 entra na página da Taylor, não no painel interno)
    "ty": {"prop": "330078762", "nome": "Taylor",
           "ct": ".*whatsapp.*|cabecalho-telefone|phone_site|.*-form|fale_conosco|agendar_visita|generate_lead|cadastre_seu_imovel"},
}

D = lambda *n: [{"name": x} for x in n]
QUERIES = {
    "cube": {"dimensions": D("date", "sessionDefaultChannelGroup", "sessionSourceMedium", "sessionCampaignName", "deviceCategory"),
             "metrics": D("sessions", "engagedSessions", "newUsers", "screenPageViews", "userEngagementDuration"), "limit": "100000"},
    "lp": {"dimensions": D("date", "landingPage"), "metrics": D("sessions", "engagedSessions", "newUsers"),
           "metricFilter": {"filter": {"fieldName": "sessions", "numericFilter": {"operation": "GREATER_THAN_OR_EQUAL", "value": {"int64Value": "3"}}}},
           "limit": "100000"},
    "ev": {"dimensions": D("date", "eventName"), "metrics": D("eventCount", "keyEvents"), "limit": "100000"},
    "utm": {"dimensions": D("date", "sessionSource", "sessionMedium", "sessionCampaignName", "sessionManualAdContent"),
            "metrics": D("sessions", "engagedSessions", "newUsers", "userEngagementDuration"), "limit": "100000"},
    "ct": {"dimensions": D("date", "eventName", "sessionDefaultChannelGroup", "sessionSourceMedium", "sessionCampaignName", "deviceCategory", "landingPage", "sessionManualAdContent"),
           "metrics": D("eventCount"), "limit": "100000"},
}


def pedido(k, q, ate="yesterday"):
    r = json.loads(json.dumps(QUERIES[q]))
    r["property"] = "properties/" + SITES[k]["prop"]
    r["dateRanges"] = [{"startDate": "2026-01-01", "endDate": ate}]
    if q == "ct":
        r["dimensionFilter"] = {"filter": {"fieldName": "eventName", "stringFilter": {"matchType": "FULL_REGEXP", "value": SITES[k]["ct"]}}}
    return r


def tabela(raw):
    """resposta do run_report → {k:[dimensões], v:[valores distintos por dimensão (menos a data)], r:[[dia, i1.., m1..]]}"""
    dims = [h["name"] for h in raw.get("dimensionHeaders", [])]
    if not dims or dims[0] != "date":
        raise ValueError("primeira dimensão não é date")
    vals = [dict() for _ in dims[1:]]
    rows = []
    for x in raw.get("rows", []):
        dv = [d["value"] for d in x["dimensionValues"]]
        d = dt.date(int(dv[0][:4]), int(dv[0][4:6]), int(dv[0][6:]))
        idx = []
        for j, v in enumerate(dv[1:]):
            m = vals[j]
            if v not in m:
                m[v] = len(m)
            idx.append(m[v])
        ms = []
        for m in x["metricValues"]:
            f = float(m["value"])
            ms.append(int(round(f)))
        rows.append([(d - BASE).days] + idx + ms)
    if int(raw.get("rowCount", len(rows))) > len(rows):
        raise ValueError(f"resposta paginada: {raw.get('rowCount')} linhas, vieram {len(rows)}")
    rows.sort()
    return {"k": dims, "v": [list(m.keys()) for m in vals], "r": rows}


import re
TOPO = 300  # páginas de destino guardadas uma a uma (por sessões no ano); as demais viram grupos pelo começo do caminho


def grupo(p):
    if not p.startswith("/") or p == "/":
        return p
    segs = [s for s in p.split("/") if s]
    if len(segs) > 1:
        return "/" + segs[0] + "/… (demais páginas)"
    m = re.match(r"[^-,+]+[-,+]?", segs[0])
    w = m.group(0) if m else segs[0]
    return "/" + w + ("…" if w != segs[0] else "") + " (demais páginas)"


def enxugar(t):
    """Mantém as TOPO páginas com mais sessões + as que tiveram contato; o resto agrupa (o arquivo cai de ~1,6 MB)."""
    lp, ct = t["lp"], t["ct"]
    tot = {}
    for r in lp["r"]:
        tot[r[1]] = tot.get(r[1], 0) + r[2]
    nomes = lp["v"][0]
    manter = {nomes[i] for i, _ in sorted(tot.items(), key=lambda x: -x[1])[:TOPO]}
    ic = ct["k"].index("landingPage") - 1
    manter |= {ct["v"][ic][r[ic + 1]] for r in ct["r"]}

    def remap(tab, j):
        velhos = tab["v"][j]
        novos, idx = {}, []
        for v in velhos:
            g = v if v in manter else grupo(v)
            if g not in novos:
                novos[g] = len(novos)
            idx.append(novos[g])
        agg = {}
        for r in tab["r"]:
            r = list(r)
            r[j + 1] = idx[r[j + 1]]
            nd = len(tab["k"])
            key = tuple(r[:nd])
            if key in agg:
                a = agg[key]
                for m in range(nd, len(r)):
                    a[m] += r[m]
            else:
                agg[key] = r
        tab["v"][j] = list(novos.keys())
        tab["r"] = sorted(agg.values())
    remap(lp, 0)
    remap(ct, ic)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta")
    ap.add_argument("--ate")
    ap.add_argument("--consultas", action="store_true")
    a = ap.parse_args()
    if a.consultas:
        for k in SITES:
            for q in QUERIES:
                print(f"## {k}_{q}.json\n" + json.dumps(pedido(k, q, a.ate or "yesterday"), ensure_ascii=False))
        return
    if not a.pasta:
        sys.exit("use --pasta ou --consultas")
    out = {"cfg": {k: {"prop": s["prop"], "nome": s["nome"], "ct": s["ct"]} for k, s in SITES.items()},
           "q": QUERIES, "d": {}}
    for k in SITES:
        t = {}
        for q in QUERIES:
            p = os.path.join(a.pasta, f"{k}_{q}.json")
            raw = json.load(open(p, encoding="utf-8"))
            if q == "ct" and not raw.get("rows"):
                raw.setdefault("dimensionHeaders", [{"name": n["name"]} for n in QUERIES["ct"]["dimensions"]])
            t[q] = tabela(raw)
        enxugar(t)
        if not t["cube"]["r"]:
            sys.exit(f"GA4 {k}: sem sessões em 2026")
        ult = BASE + dt.timedelta(days=max(r[0] for r in t["cube"]["r"]))
        ses = sum(r[5] for r in t["cube"]["r"])
        ct = sum(r[-1] for r in t["ct"]["r"])
        print(f"GA4 {SITES[k]['nome']}: último dia {ult}, {ses} sessões, {ct} contatos, linhas cube {len(t['cube']['r'])} lp {len(t['lp']['r'])} ev {len(t['ev']['r'])} ct {len(t['ct']['r'])}")
        if a.ate and ult < dt.date.fromisoformat(a.ate):
            print(f"  aviso: GA4 {SITES[k]['nome']} parado em {ult} (o painel mostra o alerta)")
        out["d"][k] = t
    out["at"] = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    os.makedirs(os.path.join(RAIZ, "dados"), exist_ok=True)
    p = os.path.join(RAIZ, "dados", "ga4.json")
    json.dump(out, open(p, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(f"dados/ga4.json gravado ({os.path.getsize(p)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
