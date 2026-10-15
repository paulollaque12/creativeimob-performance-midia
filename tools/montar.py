#!/usr/bin/env python3
"""Monta docs/index.html a partir do template e das planilhas de cada cliente.

Uso:
  python3 tools/montar.py --sh <json> --nsp <json> --lp <json> --ty <json> [--ate AAAA-MM-DD] [--artefato caminho.html]

Cada <json> é a resposta do conector Google Sheets (get_values) salva em arquivo:
{"range": "...", "values": [[cabecalho...], [linha...], ...]}

Planilhas e abas (ver README.md):
  sh  → [BaseData] SH Prime - Meta        · Meta!A1:Q40000
  nsp → [BaseData] Nova São Paulo - Meta  · Meta!A1:Q40000
  lp  → [BaseData] Lopes Prime - Meta     · Meta!A1:Q40000
  ty  → [TAYLOR] report semanal           · '[BASE] meta'!A1:R40000

Regras (iguais às do painel):
- colunas localizadas pelo nome do cabeçalho (português ou inglês);
- só 2026 (data >= 2026-01-01); números em texto pt-BR ("1.036", "12,65");
- formato compacto {c,g,a,r} com r = [dia desde 2024-01-01, iCamp, iConj, iAnuncio,
  invest_centavos, imp, cliques_link, cliques, formulario, whatsapp, leads].
"""
import argparse, datetime as dt, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = dt.date(2024, 1, 1)
CLIENTES = [("sh", "SH Prime"), ("nsp", "Nova SP"), ("lp", "Lopes Prime"), ("ty", "Taylor")]
COLS = {"d": ("Data", "Date"), "c": ("Campaign", "Campaign Name"), "g": ("Ad Group", "Adset Name"), "a": ("Ad Name",),
        "inv": ("Investimento", "Spend (Cost, Amount Spent)"), "imp": ("Impressões", "Impressions"), "clk": ("Cliques", "Clicks"),
        "lclk": ("Link Cliques", "Action Link Clicks"), "form": ("Formulario", "Formulário"), "msg": ("Mensagem",), "leads": ("Leads",)}


def num(x):
    x = str(x or "").strip()
    return float(x.replace(".", "").replace(",", ".")) if x else 0.0


def compactar(caminho, nome):
    v = json.load(open(caminho, encoding="utf-8"))["values"]
    h = [str(s).strip() for s in v[0]]
    K = {}
    for k, nomes in COLS.items():
        i = next((h.index(n) for n in nomes if n in h), -1)
        if i < 0:
            sys.exit(f"[{nome}] coluna não encontrada no cabeçalho: {nomes[0]}")
        K[k] = i
    idx = [{}, {}, {}]
    def ix(m, k):
        if k not in m:
            m[k] = len(m)
        return m[k]
    r = []
    for x in v[1:]:
        if not x:
            continue
        x = x + [""] * (len(h) - len(x))
        d = x[K["d"]]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d or "") or d < "2026-01-01":
            continue
        r.append([(dt.date.fromisoformat(d) - BASE).days, ix(idx[0], x[K["c"]] or "(sem nome)"), ix(idx[1], x[K["g"]] or "(sem nome)"),
                  ix(idx[2], x[K["a"]] or "(sem nome)"), round(num(x[K["inv"]]) * 100), int(num(x[K["imp"]])), int(num(x[K["lclk"]])),
                  int(num(x[K["clk"]])), int(num(x[K["form"]])), int(num(x[K["msg"]])), int(num(x[K["leads"]]))])
    if not r:
        sys.exit(f"[{nome}] nenhuma linha de 2026")
    ordem = lambda m: sorted(m, key=m.get)
    ult = BASE + dt.timedelta(days=max(z[0] for z in r))
    print(f"[{nome}] {len(r)} linhas de 2026 · até {ult.isoformat()} · {len(idx[0])} campanhas · "
          f"R$ {sum(z[4] for z in r)/100:,.2f} · leads {sum(z[10] for z in r)}")
    return {"c": ordem(idx[0]), "g": ordem(idx[1]), "a": ordem(idx[2]), "r": r}, ult


def main():
    ap = argparse.ArgumentParser()
    for k, _ in CLIENTES:
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--ate", help="último dia esperado (AAAA-MM-DD); falha se alguma base estiver atrás")
    ap.add_argument("--artefato", help="também grava a versão para o artefato do Claude (sem o esqueleto <html>)")
    a = ap.parse_args()
    dados, ults = {}, {}
    for k, nome in CLIENTES:
        dados[k], ults[k] = compactar(getattr(a, k), nome)
    if a.ate:
        alvo = dt.date.fromisoformat(a.ate)
        atras = {n: ults[k] for k, n in CLIENTES if ults[k] < alvo}
        if atras:
            sys.exit(f"Base atrasada (esperado {alvo}): " + ", ".join(f"{n} até {d}" for n, d in atras.items()) + ". Nada foi publicado.")
    agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    t = open(os.path.join(RAIZ, "fonte", "template.html"), encoding="utf-8").read()
    js = lambda d: json.dumps(d, separators=(",", ":"), ensure_ascii=False)
    for k, _ in CLIENTES:
        marca = f"/*__DATA_{k.upper()}__*/null"
        if marca not in t:
            sys.exit(f"template sem o marcador {marca}")
        t = t.replace(marca, js(dados[k]))
    t = t.replace("/*__AT__*/", agora)
    if a.artefato:
        open(a.artefato, "w", encoding="utf-8").write(t)
        print(f"artefato gravado em {a.artefato}")
    cabeca = "".join(re.findall(r"<title>.*?</title>\n?|<link [^>]*>\n?", t[:4000]))
    corpo = re.sub(r"<title>.*?</title>\n?|<link [^>]*>\n?", "", t[:4000]) + t[4000:]
    pagina = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
              '<meta name="robots" content="noindex,nofollow">' + cabeca +
              '<style>body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
              '</head><body>' + corpo + '</body></html>')
    open(os.path.join(RAIZ, "docs", "index.html"), "w", encoding="utf-8").write(pagina)
    print(f"docs/index.html gerado ({len(pagina)/1024:.0f} KB) · atualizado em {agora}")


if __name__ == "__main__":
    main()
