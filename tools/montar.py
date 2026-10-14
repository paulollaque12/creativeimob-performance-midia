#!/usr/bin/env python3
"""Monta docs/index.html a partir do template e das planilhas [BaseData] (aba Meta).

Uso:
  python3 tools/montar.py --sh <json_sh> --nsp <json_nsp> [--ate AAAA-MM-DD]

Cada <json_*> é a resposta do conector Google Sheets (get_values, range Meta!A1:Q40000):
{"range": "...", "values": [[cabecalho...], [linha...], ...]}

Regras (iguais às do painel):
- só 2026 (data >= 2026-01-01);
- números em texto pt-BR ("1.036", "12,65");
- Investimento = col H, Impressões = I, Cliques = J, Link Cliques = K, Formulário = O, Mensagem = P, Leads = Q;
- formato compacto: {c,g,a,r} com r = [dia desde 2024-01-01, iCamp, iConj, iAnuncio, invest_centavos, imp, cliques_link, cliques, form, whatsapp, leads].
"""
import argparse, datetime as dt, json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = dt.date(2024, 1, 1)
CAB = ["Data", "ID Campaign", "Campaign", "ID Ad Group", "Ad Group", "ID Ad", "Ad Name", "Investimento", "Impressões",
       "Cliques", "Link Cliques", "Leads Meta", "Leads Site", "Mensagens", "Formulario", "Mensagem", "Leads"]


def num(x):
    x = str(x or "").strip()
    if not x:
        return 0.0
    return float(x.replace(".", "").replace(",", "."))


def compactar(caminho, nome):
    v = json.load(open(caminho, encoding="utf-8"))["values"]
    if v[0][:17] != CAB:
        sys.exit(f"[{nome}] cabeçalho inesperado: {v[0][:17]}")
    idx = [{}, {}, {}]
    def ix(m, k):
        if k not in m:
            m[k] = len(m)
        return m[k]
    r = []
    for x in v[1:]:
        if not x or not x[0] or x[0] < "2026-01-01":
            continue
        x = x + [""] * (17 - len(x))
        r.append([(dt.date.fromisoformat(x[0]) - BASE).days, ix(idx[0], x[2]), ix(idx[1], x[4]), ix(idx[2], x[6]),
                  round(num(x[7]) * 100), int(num(x[8])), int(num(x[10])), int(num(x[9])),
                  int(num(x[14])), int(num(x[15])), int(num(x[16]))])
    if not r:
        sys.exit(f"[{nome}] nenhuma linha de 2026")
    ordem = lambda m: sorted(m, key=m.get)
    ult = BASE + dt.timedelta(days=max(z[0] for z in r))
    inv = sum(z[4] for z in r) / 100
    print(f"[{nome}] {len(r)} linhas de 2026 · até {ult.isoformat()} · {len(idx[0])} campanhas · R$ {inv:,.2f} · leads {sum(z[10] for z in r)}")
    return {"c": ordem(idx[0]), "g": ordem(idx[1]), "a": ordem(idx[2]), "r": r}, ult


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sh", required=True)
    ap.add_argument("--nsp", required=True)
    ap.add_argument("--ate", help="data mínima esperada do último dia (AAAA-MM-DD); falha se alguma base estiver atrás")
    a = ap.parse_args()
    sh, u1 = compactar(a.sh, "SH Prime")
    nsp, u2 = compactar(a.nsp, "Nova SP")
    if a.ate:
        alvo = dt.date.fromisoformat(a.ate)
        if u1 < alvo or u2 < alvo:
            sys.exit(f"Base atrasada: SH Prime até {u1}, Nova SP até {u2}, esperado {alvo}. Nada foi publicado.")
    agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    t = open(os.path.join(RAIZ, "fonte", "template.html"), encoding="utf-8").read()
    for marca in ("/*__DATA_SH__*/null", "/*__DATA_NSP__*/null", "/*__AT__*/"):
        if marca not in t:
            sys.exit(f"template sem o marcador {marca}")
    js = lambda d: json.dumps(d, separators=(",", ":"), ensure_ascii=False)
    t = t.replace("/*__DATA_SH__*/null", js(sh)).replace("/*__DATA_NSP__*/null", js(nsp)).replace("/*__AT__*/", agora)
    # versão pública: documento completo (GitHub Pages não acrescenta o esqueleto do artefato)
    import re
    cabeca = "".join(re.findall(r"<title>.*?</title>\n?|<link [^>]*>\n?", t[:4000]))
    corpo = re.sub(r"<title>.*?</title>\n?|<link [^>]*>\n?", "", t[:4000], count=0) + t[4000:]
    pagina = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
              '<meta name="robots" content="noindex,nofollow">' + cabeca +
              '<style>body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
              '</head><body>' + corpo + '</body></html>')
    out = os.path.join(RAIZ, "docs", "index.html")
    open(out, "w", encoding="utf-8").write(pagina)
    print(f"docs/index.html gerado ({len(pagina)/1024:.0f} KB) · atualizado em {agora}")


if __name__ == "__main__":
    main()
