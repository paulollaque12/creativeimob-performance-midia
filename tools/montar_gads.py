#!/usr/bin/env python3
"""Monta docs/taylor/google/index.html (performance.creativeimob.app/taylor/google/) direto do conector Google Ads.

Uso:
  python3 tools/montar_gads.py --dir /tmp/gads [--ate AAAA-MM-DD]

Arquivos esperados em --dir (respostas salvas de mcp__Google_Ads__search_search, conta Taylor 5451475929,
login_customer_id 4498709696, período 2026-01-01..ONTEM, todos com limit 10000):
  ads.json    resource ad_group_ad · fields segments.date, campaign.name, ad_group.name, ad_group_ad.ad.id,
              ad_group_ad.ad.name, metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions
              · conditions metrics.impressions > 0
  camp.json   resource campaign · fields segments.date, campaign.id, campaign.name, campaign.advertising_channel_type,
              metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions · impressions > 0
              (a diferença campanha − anúncios vira a linha "(Performance Max / sem anúncio)")
  adinfo.json resource ad_group_ad · fields ad_group_ad.ad.id, .ad.type, .ad.name, .ad.final_urls,
              .ad.responsive_search_ad.headlines · impressions > 0 (rótulo dos anúncios sem nome)
  kw.json     resource keyword_view · fields segments.date, campaign.name, ad_group.id, ad_group.name,
              ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
              metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.top_impression_percentage,
              metrics.search_top_impression_share · impressions > 0
  conv_ad.json   ad_group_ad · segments.date, ad_group_ad.ad.id, segments.conversion_action_name, metrics.conversions · conversions > 0
  conv_camp.json campaign · segments.date, campaign.name, segments.conversion_action_name, metrics.conversions · conversions > 0
  conv_kw.json   keyword_view · segments.date, ad_group_criterion.criterion_id, ad_group.id, segments.conversion_action_name,
                 metrics.conversions · conversions > 0
  (as três de conversão costumam vir inline: gravar o JSON da resposta no arquivo)

Regras: Investimento = cost_micros/1e6; Cliques = clicks (no Google não há "cliques no link"; CTR = cliques ÷ impressões,
como no Looker); Leads = conversões de Formulário + WhatsApp (ação com "whats" no nome = WhatsApp; "Rota" = pedido de
rota no mapa, NÃO é lead; o resto = Formulário). IS sup. = impressões no topo ÷ impressões elegíveis no topo
(top_impression_percentage × impressões ÷ search_top_impression_share), agregado das palavras-chave.
"""
import argparse, ast, collections, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar  # noqa: E402


def ler(p):
    o = json.load(open(p, encoding="utf-8"))
    if isinstance(o, dict) and "results" in o:
        o = o["results"]
    return o


def classe(nome):
    n = (nome or "").lower()
    if "whats" in n or "zap" in n:
        return "W"
    if "rota" in n or "direction" in n:
        return "R"
    return "F"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="/tmp/gads")
    ap.add_argument("--ate")
    a = ap.parse_args()
    D = lambda n: ler(os.path.join(a.dir, n))
    ads, camp, info, kw = D("ads.json"), D("camp.json"), D("adinfo.json"), D("kw.json")
    cad, ccamp, ckw = D("conv_ad.json"), D("conv_camp.json"), D("conv_kw.json")

    # rótulo dos anúncios
    lab = {}
    for x in info:
        i = int(x["ad_group_ad.ad.id"])
        nm = (x.get("ad_group_ad.ad.name") or "").strip()
        if not nm:
            hs = x.get("ad_group_ad.ad.responsive_search_ad.headlines")
            try:
                hs = ast.literal_eval(hs) if isinstance(hs, str) else (hs or [])
            except Exception:
                hs = []
            txt = [h.get("text", "") for h in hs if isinstance(h, dict)][:2]
            if txt:
                nm = "RSA · " + " | ".join(txt)
            else:
                urls = x.get("ad_group_ad.ad.final_urls") or ""
                m = re.findall(r"https?://[^'\" ,\]]+", str(urls))
                tp = {"HTML5_UPLOAD_AD": "Display HTML5", "RESPONSIVE_DISPLAY_AD": "Display responsivo"}.get(x.get("ad_group_ad.ad.type"), "Anúncio")
                nm = tp + (" · " + m[0].rstrip("/").split("/")[-1] if m else "")
        lab[i] = f"{nm} · #{str(i)[-5:]}"

    # conversões por linha (W/F), sem "Rota"
    cv_ad = collections.defaultdict(lambda: [0.0, 0.0])
    for x in cad:
        c = classe(x["segments.conversion_action_name"])
        if c == "R":
            continue
        cv_ad[(x["segments.date"], int(x["ad_group_ad.ad.id"]))][0 if c == "F" else 1] += float(x["metrics.conversions"])
    cv_camp = collections.defaultdict(lambda: [0.0, 0.0])
    for x in ccamp:
        c = classe(x["segments.conversion_action_name"])
        if c == "R":
            continue
        cv_camp[(x["segments.date"], x["campaign.name"])][0 if c == "F" else 1] += float(x["metrics.conversions"])
    cv_kw = collections.defaultdict(lambda: [0.0, 0.0])
    for x in ckw:
        c = classe(x["segments.conversion_action_name"])
        if c == "R":
            continue
        cv_kw[(x["segments.date"], int(x["ad_group_criterion.criterion_id"]), int(x["ad_group.id"]))][0 if c == "F" else 1] += float(x["metrics.conversions"])

    idx = [{}, {}, {}, {}]
    def ix(m, k):
        if k not in m:
            m[k] = len(m)
        return m[k]
    day = lambda d: (dt.date.fromisoformat(d) - montar.BASE).days
    r = []
    soma = collections.defaultdict(lambda: [0, 0, 0, 0.0, 0.0])  # por (data, campanha): micros, imp, clk, form, msg
    for x in ads:
        d = x["segments.date"]
        if d < "2026-01-01":
            continue
        cn, i = x["campaign.name"], int(x["ad_group_ad.ad.id"])
        f, w = cv_ad.get((d, i), (0.0, 0.0))
        mic, imp, clk = int(x["metrics.cost_micros"]), int(x["metrics.impressions"]), int(x["metrics.clicks"])
        s = soma[(d, cn)]; s[0] += mic; s[1] += imp; s[2] += clk; s[3] += f; s[4] += w
        r.append([day(d), ix(idx[0], cn), ix(idx[1], x["ad_group.name"] or "(sem grupo)"), ix(idx[2], lab.get(i, f"Anúncio · #{str(i)[-5:]}")),
                  round(mic / 1e4), imp, clk, clk, round(f, 3), round(w, 3), round(f + w, 3)])
    # resíduo por campanha/dia (Performance Max e o que não tem anúncio)
    for x in camp:
        d = x["segments.date"]
        if d < "2026-01-01":
            continue
        cn = x["campaign.name"]
        s = soma.get((d, cn), [0, 0, 0, 0.0, 0.0])
        mic, imp, clk = int(x["metrics.cost_micros"]) - s[0], int(x["metrics.impressions"]) - s[1], int(x["metrics.clicks"]) - s[2]
        cf, cw = cv_camp.get((d, cn), (0.0, 0.0))
        f, w = max(0.0, cf - s[3]), max(0.0, cw - s[4])
        if mic <= 0 and imp <= 0 and f + w < 1e-6:
            continue
        tp = "Performance Max" if x.get("campaign.advertising_channel_type") == "PERFORMANCE_MAX" else "Sem anúncio"
        r.append([day(d), ix(idx[0], cn), ix(idx[1], f"({tp})"), ix(idx[2], f"({tp} · sem detalhe por anúncio)"),
                  round(max(mic, 0) / 1e4), max(imp, 0), max(clk, 0), max(clk, 0), round(f, 3), round(w, 3), round(f + w, 3)])
    r.sort()

    # palavras-chave
    MT = {"EXACT": "exata", "PHRASE": "frase", "BROAD": "ampla"}
    kr = []
    for x in kw:
        d = x["segments.date"]
        if d < "2026-01-01":
            continue
        cid, gid = int(x["ad_group_criterion.criterion_id"]), int(x["ad_group.id"])
        txt = f'{x["ad_group_criterion.keyword.text"]} · {MT.get(x["ad_group_criterion.keyword.match_type"], str(x["ad_group_criterion.keyword.match_type"]).lower())}'
        imp, clk = int(x["metrics.impressions"]), int(x["metrics.clicks"])
        tip = float(x.get("metrics.top_impression_percentage") or 0)
        sis = float(x.get("metrics.search_top_impression_share") or 0)
        top = tip * imp
        elig = top / sis if sis > 0 else 0.0
        f, w = cv_kw.get((d, cid, gid), (0.0, 0.0))
        kr.append([day(d), ix(idx[0], x["campaign.name"]), ix(idx[1], x["ad_group.name"]), ix(idx[3], txt),
                   round(int(x["metrics.cost_micros"]) / 1e4), imp, clk, clk, round(f, 3), round(w, 3), round(f + w, 3), round(top, 2), round(elig, 2)])
    kr.sort()

    ult = dt.date.fromordinal(montar.BASE.toordinal() + max(z[0] for z in r)).isoformat()
    if a.ate and ult < a.ate:
        sys.exit(f"Google Ads só até {ult} (esperado {a.ate}). Nada foi gerado.")
    ordem = lambda m: sorted(m, key=m.get)
    dados = {"ty": {"c": ordem(idx[0]), "g": ordem(idx[1]), "a": ordem(idx[2]), "k": ordem(idx[3]), "r": r, "kr": kr}}
    tot = lambda j: sum(z[j] for z in r)
    print(f"[Taylor · Google Ads] {len(r)} linhas · até {ult} · {len(idx[0])} campanhas · R$ {tot(4)/100:,.2f} · "
          f"cliques {tot(6)} · leads {tot(10):.1f} (form. {tot(8):.1f}, WhatsApp {tot(9):.1f}) · {len(idx[3])} palavras-chave ({len(kr)} linhas)")
    agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    montar.solo(agora, dados, "ty", os.path.join("taylor", "google"), "Taylor Imóveis · Performance Google Ads",
                fonte="Fonte: Google Ads, conta Taylor Imóveis 5451475929 (leitura direta do conector do Google Ads)",
                trocas=TROCAS_GOOGLE, plat="g", raiz="../../",
                nav=PLAT_NAV.format(meta="../", am="", gads="./", ag=' aria-current="page"'))


PLAT_NAV = ('<nav class="plat" aria-label="Plataforma"><a href="{meta}"{am}>Meta Ads</a>'
            '<a href="{gads}"{ag}>Google Ads</a></nav>')

TROCAS_GOOGLE = [
    ("1iNZ5W8qUInPaw87_hG-nLwlB1pNubzW32PsfUi0qnTM", ""),
    ("Meta Ads", "Google Ads"),
    ("da veiculação no Meta.", "da veiculação no Google Ads."),
    ("Cadastros feitos no formulário nativo do Meta.", "Formulários enviados no site, registrados como conversão no Google Ads."),
    ("Conversas iniciadas pelo botão de mensagem.", "Contatos por WhatsApp registrados como conversão no site."),
    ("Divisão entre o formulário nativo e as conversas por WhatsApp.", "Divisão das conversões entre formulários do site e contatos por WhatsApp."),
    ("Cliques no link", "Cliques"),
    ('const LVG="Conjunto";', 'const LVG="Grupo de anúncios";'),
    ('data-l="g" aria-pressed="false">Conjunto</button>', 'data-l="g" aria-pressed="false">Grupo</button>'),
    ('["Tx. conv. (lead ÷ impressão)"', '["Tx. de conversão"'),
    ("Detalhes por campanha, conjunto e anúncio", "Detalhes por campanha, grupo, anúncio e palavra-chave"),
    ("Cliques = cliques no link. Tx. conv. = leads ÷ impressões.", "Cliques = cliques nos anúncios. Leads = conversões de formulário e WhatsApp (pedidos de rota não contam). IS sup. = parcela de impressões no topo da pesquisa. Tx. conv. = leads ÷ impressões."),
]

if __name__ == "__main__":
    main()
