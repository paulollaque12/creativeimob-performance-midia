#!/usr/bin/env python3
"""Monta docs/dupllex/index.html (performance.creativeimob.app/dupllex/): página da Dupllex Imóveis.

Uso:
  python3 tools/montar_dupllex.py [--gads /tmp/dx/gads] [--ga /tmp/dx/ga] [--ate AAAA-MM-DD]

Fontes (conectores oficiais):
- Google Ads: conta "Dupllex" 1381273646, login_customer_id 4498709696 (MCC CREATIVEIMOB), as 7 consultas de
  tools/montar_gads.py (ads, camp, adinfo, kw, conv_ad, conv_camp, conv_kw) em --gads. Em 2026 só há uma
  Performance Max (19/08 a 10/09/2026, sem conversões): as consultas por anúncio e palavra-chave voltam vazias.
- GA4: propriedade "dupllex.com.br" 529313528 (achada pelas conversões GA4 importadas no Google Ads). As 5 consultas
  de tools/ga4.py em --ga como dx_<consulta>.json, com UMA diferença no `ct`: filtro eventName EXACT generate_lead e
  9ª dimensão customEvent:lead_method; aqui o método vira o nome do evento (generate_lead_whatsapp / _formulario),
  para o tipo de contato sair certo. Contatos no site = generate_lead (evento-chave do site; contact_click não conta,
  porque o clique no WhatsApp que vira lead já dispara generate_lead com lead_method=whatsapp).
- Meta Ads: conta "Dupllex" 1405527677145000 (BM Dupllex.imoveis) ainda NÃO liberada no conector da Meta
  (rollout gradual). Sem Meta, a página sai sem o botão Meta Ads (Overview | Google Ads | GA4). Quando liberar,
  ler como a Montreal (montar_montreal.ler_meta) e passar o modelo em `dm`.

Reaproveita a estrutura da Taylor no template (chave "ty") e troca a identidade no arquivo gerado, como a Montreal:
site dupllex.com.br = monocromático (grafite #212121, branco #FAFAFA, cinza #7A7A7A, borda #DBDBDA), títulos em
Pragmatica Extended (Adobe) → aqui Archivo expandida (Google Fonts), cantos retos. Acento em pedra/greige (#A79F92).
"""
import argparse, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar  # noqa: E402
import montar_gads  # noqa: E402
import montar_meta  # noqa: E402
import ga4  # noqa: E402

PASTA = "dupllex"
TITULO = "Dupllex · Performance de mídia"
FONTE_META = "Fonte: planilha [BaseData] Dupllex · Meta (provisória até o conector oficial da Meta liberar a conta 1405527677145000)"
PLANILHA_META = "1_eOdkIvt7JALyZeI5LBQ6HP9gqzQPKq8i1-WSQ-5Sg4"  # aba Meta, mesmo formato das BaseData do painel interno
CACHE_M = os.path.join(montar.RAIZ, "dados", "dupllex_meta.json")
FONTE_GADS = "Fonte: Google Ads, conta Dupllex 1381273646 (leitura direta do conector do Google Ads)"
CACHE_G = os.path.join(montar.RAIZ, "dados", "dupllex_gads.json")
CACHE_GA = os.path.join(montar.RAIZ, "dados", "dupllex_ga4.json")
LOGO = os.path.join(montar.RAIZ, "fonte", "dupllex_logo.json")  # máscara PNG (base64) do logo enviado em 17/11/2026
GA_SITE = {"prop": "529313528", "nome": "Dupllex", "ct": "generate_lead.*"}

# ---------- identidade Dupllex ----------
FD = '"Archivo","Helvetica Neue",Arial,ui-sans-serif,system-ui,sans-serif'
TOK_CLARO = f"""--bg:#F4F4F4; --surface:#FFFFFF; --surface-2:#FAFAFA; --ink:#212121; --ink-2:#4A4A4A; --muted:#7A7A7A; --line:#DBDBDA; --line-2:#EBEBEA;
  --gold:#212121; --gold-soft:#E2E1DE; --gold-ink:#111111; --graph:#212121; --graph-ink:#FAFAFA; --on-acc:#FAFAFA; --fs3:#8C8478; --tipbg:#212121;
  --s2:#8C8478; --s2-soft:#E8E4DD; --brass:#7A7166; --brass-2:#8C8478; --r:2px;
  --f-display:{FD}; --f-text:{FD};
  --shadow:0 1px 2px rgba(0,0,0,.04),0 14px 30px -22px rgba(0,0,0,.30)"""
TOK_ESCURO = f"""--bg:#111111; --surface:#1A1A1A; --surface-2:#1F1F1F; --ink:#F4F4F4; --ink-2:#C9C9C7; --muted:#8E8E8B; --line:#2B2B2B; --line-2:#222222;
  --gold:#E9E7E2; --gold-soft:#2E2C29; --gold-ink:#FFFFFF; --graph:#212121; --graph-ink:#FAFAFA; --on-acc:#141414; --fs3:#8C8478; --tipbg:#262626;
  --s2:#B5AC9E; --s2-soft:#3A3733; --brass:#B5AC9E; --brass-2:#8C8478; --r:2px;
  --f-display:{FD}; --f-text:{FD};
  --shadow:0 1px 2px rgba(0,0,0,.4),0 16px 36px -20px rgba(0,0,0,.8)"""
CORES = [  # cores fixas do acabamento da Taylor → Dupllex (dourado vira branco/pedra, verde vira grafite)
    ("rgba(149,140,88,", "rgba(250,250,250,"), ("rgba(181,172,119,", "rgba(181,172,158,"), ("rgba(244,241,232,", "rgba(250,250,250,"),
    ("rgba(7,44,33,", "rgba(17,17,17,"), ("#958C58", "#B5AC9E"), ("#B5AC77", "#D7D1C7"), ("#D9D2A9", "#E9E5DE"), ("#D3CA94", "#CFC8BC"),
    ("#A89E66", "#E9E7E2"), ("#E4E1D6", "#B5AC9E"), ("#F4F1E8", "#FAFAFA"), ("#EEEBE2", "#E4E4E2"), ("#072C21", "#212121"),
]
CSS_EXTRA = """
/* ===== Dupllex: monocromático do site (grafite #212121 + branco), Archivo expandida como a Pragmatica Extended, cantos retos ===== */
.mk-dx{display:flex;align-items:center}
.mk-dx i{display:block;width:104px;height:38px;background:#FAFAFA;-webkit-mask:url("data:image/png;base64,__WRD__") center/contain no-repeat;mask:url("data:image/png;base64,__WRD__") center/contain no-repeat}
:root[data-client="ty"] .top{background:radial-gradient(120% 140% at 100% 0%,rgba(250,250,250,.06),transparent 46%),var(--graph)}
:root[data-client="ty"] .brand-txt h1,:root[data-client="ty"] .sh h2,:root[data-client="ty"] .plat button,:root[data-client="ty"] .ovh .t{font-stretch:125%}
:root[data-client="ty"] .brand-txt h1{font-weight:300;letter-spacing:.14em}
:root[data-client="ty"] .sh h2{font-weight:300;letter-spacing:.02em;text-transform:uppercase}
:root[data-client="ty"] .tile .v,:root[data-client="ty"] .num{font-variant-numeric:tabular-nums;font-weight:300}
:root[data-client="ty"] .chip,:root[data-client="ty"] .chip[aria-pressed=true]{letter-spacing:.1em;font-size:10.5px}
:root[data-client="ty"] .presets>.pchips{gap:22px}
"""
MARCA_TY = '<div class="mk-ty" role="img" aria-label="Taylor Imóveis"><i class="tyc"></i><i class="tyw"></i></div>'
MARCA_DX = '<div class="mk-dx" role="img" aria-label="Dupllex"><i></i></div>'


def tx():
    t = json.loads(json.dumps(montar_meta.TX))
    # Meta vinda da planilha: Leads = Formulario + Mensagem (WhatsApp), regra do painel interno; não vira "Site"
    t["m"] = [par for par in t["m"] if "WhatsApp" not in par[0] and "Conversas iniciadas" not in par[0]]
    for k in t:
        for par in t[k]:
            for j in (0, 1):
                par[j] = par[j].replace(montar_meta.FONTE_META, FONTE_META).replace(montar_meta.FONTE_GADS, FONTE_GADS)
    return t


def montar_ga(pasta, ate=None):
    """5 respostas dx_<q>.json → modelo GA4 na chave "ty" (formato de dados/ga4.json)."""
    t = {}
    for q in ga4.QUERIES:
        raw = json.load(open(os.path.join(pasta, f"dx_{q}.json"), encoding="utf-8"))
        if q == "ct":
            hs = [h["name"] for h in raw.get("dimensionHeaders", [])]
            if "customEvent:lead_method" in hs:  # resposta crua do conector: método vira o nome do evento
                j = hs.index("customEvent:lead_method")
                for r in raw.get("rows", []):
                    dv = r["dimensionValues"]
                    dv[1]["value"] = "generate_lead_" + (dv[j]["value"] if dv[j]["value"] not in ("", "(not set)") else "outro")
                    del dv[j]
                del raw["dimensionHeaders"][j]
            if not raw.get("rows"):
                raw.setdefault("dimensionHeaders", [{"name": n["name"]} for n in ga4.QUERIES["ct"]["dimensions"]])
        t[q] = ga4.tabela(raw)
    ga4.enxugar(t)
    ult = ga4.BASE + dt.timedelta(days=max(r[0] for r in t["cube"]["r"]))
    print(f"[Dupllex · GA4] último dia {ult}, {sum(r[5] for r in t['cube']['r'])} sessões, {sum(r[-1] for r in t['ct']['r'])} contatos")
    if ate and str(ult) < ate:
        print(f"AVISO: GA4 só até {ult} (esperado {ate})")
    out = {"cfg": {"ty": GA_SITE}, "q": ga4.QUERIES, "d": {"ty": t},
           "at": dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")}
    json.dump(out, open(CACHE_GA, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    return out


def identidade(html):
    lg = json.load(open(LOGO, encoding="utf-8"))
    i0, i1 = html.index("<style>", html.index("</head>")), html.index("</style>", html.index("</head>"))
    css = html[i0:i1]
    css, n1 = re.subn(r':root\[data-client="ty"\]\{[^}]*\}', lambda m: ':root[data-client="ty"]{\n  ' + TOK_CLARO + "}", css, count=1)
    css, n2 = re.subn(r'(:root\[data-client="ty"\]:not\(\[data-theme="light"\]\)\{)[^}]*\}', lambda m: m.group(1) + "\n  " + TOK_ESCURO + "}", css, count=1)
    css, n3 = re.subn(r'(:root\[data-client="ty"\]\[data-theme="dark"\]\{)[^}]*\}', lambda m: m.group(1) + "\n  " + TOK_ESCURO + "}", css, count=1)
    if not (n1 and n2 and n3):
        sys.exit("[dupllex] blocos de tokens da Taylor não encontrados no template")
    for a, b in CORES:
        css = css.replace(a, b).replace(a.lower(), b)
    css += CSS_EXTRA.replace("__WRD__", lg["wrd"])
    html = html[:i0] + css + html[i1:]
    html, n = re.subn(r"family=Josefin\+Sans:wght@[0-9;]+&family=Inter:wght@[0-9;]+", "family=Archivo:wdth,wght@100..125,200..700", html)
    if not n:
        sys.exit("[dupllex] link das fontes não encontrado")
    html = re.sub(r'<option value="0">SH Prime</option>.*?<option value="3">Taylor</option>', "", html, count=1, flags=re.S)
    html = re.sub(r"Fonte: planilhas \[BaseData\][^<]*", "", html, count=1)
    html = re.sub(r"/\*[^*]*?(Taylor|taylor)[^*]*?\*/", "", html)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ate")
    ap.add_argument("--gads")
    ap.add_argument("--ga")
    ap.add_argument("--meta", help="get_values da aba Meta da planilha (JSON com cabeçalho na 1ª linha)")
    a = ap.parse_args()
    if a.meta:  # provisório: planilha BaseData até o conector da Meta liberar a conta
        dm, ult_m = montar.compactar(a.meta, "Dupllex · Meta (planilha)")
        if a.ate and str(ult_m) < a.ate:
            print(f"AVISO: planilha da Meta só até {ult_m} (esperado {a.ate})")
        json.dump(dm, open(CACHE_M, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    elif os.path.exists(CACHE_M):
        dm = json.load(open(CACHE_M, encoding="utf-8"))
        print("Meta: usando a última cópia em dados/dupllex_meta.json")
    else:
        dm = {"c": [], "g": [], "a": [], "r": []}
    if a.gads:
        snap_g, ult_g, resumo = montar_gads.construir(a.gads)
        print(resumo.replace("Taylor", "Dupllex"))
        json.dump(snap_g, open(CACHE_G, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    else:
        snap_g = json.load(open(CACHE_G, encoding="utf-8"))
        print("Google Ads: usando a última cópia em dados/dupllex_gads.json")
    if a.ga:
        ga = montar_ga(a.ga, a.ate)
    else:
        ga = json.load(open(CACHE_GA, encoding="utf-8"))
        print("GA4: usando a última cópia em dados/dupllex_ga4.json")
    tem_m = bool(dm["r"])
    nav = (montar_meta.NAV_O + montar_meta.NAV_G + (montar_meta.NAV_I.replace(' aria-pressed="true"', ' aria-pressed="false"') if tem_m else "")
           + montar_meta.NAV_A + "</nav>")  # mesma ordem da Taylor: Overview, Google Ads, Meta Ads, GA4
    sem_meta = [
        ("Meta, Google e site no mesmo período", "Google Ads e site no mesmo período"),
        ("a verba somada de Meta Ads e Google Ads, os leads", "a verba do Google Ads, os leads"),
        ("Meta Ads, Google Ads e site no mesmo período", "Google Ads e site no mesmo período"),
        ("Fontes: Meta Ads e Google Ads (conectores oficiais) e Google Analytics 4 do site, somente 2026. Leads = leads da Meta + conversões do Google Ads. Contatos no site = WhatsApp, telefone e formulário registrados pelo GA4.",
         "Fontes: Google Ads (conector oficial) e Google Analytics 4 do site, somente 2026. Leads = conversões do Google Ads. Contatos no site = leads do site (evento generate_lead do GA4: formulário e WhatsApp)."),
    ]
    com_meta = [
        ("Fontes: Meta Ads e Google Ads (conectores oficiais) e Google Analytics 4 do site, somente 2026. Leads = leads da Meta + conversões do Google Ads. Contatos no site = WhatsApp, telefone e formulário registrados pelo GA4.",
         "Fontes: Meta Ads (planilha BaseData, provisória até o conector oficial liberar a conta), Google Ads (conector oficial) e Google Analytics 4 do site, somente 2026. Leads = leads da Meta (formulário + WhatsApp) + conversões do Google Ads. Contatos no site = leads do site (evento generate_lead do GA4: formulário e WhatsApp)."),
    ]
    trocas = [(montar_meta.PLANILHA_TY, ""), (MARCA_TY, MARCA_DX), ('name:"Taylor"', 'name:"Dupllex"'), ('ty:"Taylor"', 'ty:"Dupllex"'),
              ("com a Taylor", "com a Dupllex")] + (com_meta if tem_m else sem_meta)
    agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    montar.solo(agora, {"ty": dm}, "ty", PASTA, TITULO, fonte=FONTE_META if tem_m else FONTE_GADS, nav=nav, snap_g=snap_g, tx=tx(), ga=ga, trocas=trocas)
    p = os.path.join(montar.RAIZ, "docs", PASTA, "index.html")
    html = identidade(open(p, encoding="utf-8").read())
    resto = [w for w in ("Taylor", "taylor", "TAYLOR") if w in re.sub(r"<style>.*?</style>", "", html, flags=re.S)]
    if resto:
        print("AVISO: ainda há menções a", resto)
    open(p, "w", encoding="utf-8").write(html)
    print(f"docs/{PASTA}/index.html pronto ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
