#!/usr/bin/env python3
"""Monta docs/montreal/index.html (performance.creativeimob.app/montreal/): página da Montreal Business Imóveis.

Uso:
  python3 tools/montar_montreal.py [--gads /tmp/mt/gads] [--ate AAAA-MM-DD] /tmp/mt/meta/*.json

Fontes (conectores oficiais, mesmas consultas da Taylor; ver tools/montar_meta.py e tools/montar_gads.py):
- Meta Ads: conta "C.A. Montreal Business Imob" 1210410723539965 (BM Montreal Business), um mês por chamada,
  level=ad, time_increment="1", mesmos campos e filtro da Taylor.
- Google Ads: conta "Montreal Business Imóveis" 6154519094, login_customer_id 4498709696 (MCC CREATIVEIMOB),
  as 7 consultas de tools/montar_gads.py (ads, camp, adinfo, kw, conv_ad, conv_camp, conv_kw).
- GA4: ainda sem acesso (propriedades 290629683, 258046319 e 508560208 vinculadas ao Google Ads respondem "sem permissão").
  Sem dados/montreal_ga4.json a página sai sem o botão GA4 e a Overview troca os cartões do site por Impressões e CTR.

A página reaproveita a estrutura da Taylor no template (chave "ty": Overview, Meta, Google, abas e acabamento) e troca
a identidade no arquivo gerado: tokens de cor, cores fixas do acabamento, cantos, fonte e marca (site montrealbusiness.com.br:
turquesa #13D1D1, grafite #374151/#1F2937/#111827, Plus Jakarta Sans). Nada da Taylor fica visível nem nos dados.
"""
import argparse, base64, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar  # noqa: E402
import montar_gads  # noqa: E402
import montar_meta  # noqa: E402

PASTA = "montreal"
TITULO = "Montreal Business · Performance de mídia"
FONTE_META = "Fonte: Meta Ads, conta C.A. Montreal Business Imob (leitura direta do conector oficial da Meta)"
FONTE_GADS = "Fonte: Google Ads, conta Montreal Business Imóveis 6154519094 (leitura direta do conector do Google Ads)"
CACHE_G = os.path.join(montar.RAIZ, "dados", "montreal_gads.json")
CACHE_GA = os.path.join(montar.RAIZ, "dados", "montreal_ga4.json")
LOGO = os.path.join(montar.RAIZ, "fonte", "montreal_logo.json")  # máscaras PNG (base64) do ícone e do nome

# ---------- identidade Montreal ----------
TOK_CLARO = """--bg:#F4F6F8; --surface:#FFFFFF; --surface-2:#F9FAFB; --ink:#111827; --ink-2:#4B5563; --muted:#6B7280; --line:#E5E7EB; --line-2:#EEF0F3;
  --gold:#13C4C4; --gold-soft:#D3F4F4; --gold-ink:#087F7F; --graph:#1F2937; --graph-ink:#F3F6F8; --on-acc:#04292A; --fs3:#374151; --tipbg:#1F2937;
  --s2:#374151; --s2-soft:#E5E7EB; --brass:#0B9A9A; --brass-2:#9CA3AF; --r:12px;
  --f-display:"Plus Jakarta Sans","Roboto",ui-sans-serif,system-ui,sans-serif; --f-text:"Plus Jakarta Sans","Roboto",ui-sans-serif,system-ui,sans-serif;
  --shadow:0 1px 2px rgba(17,24,39,.05),0 14px 30px -20px rgba(17,24,39,.28)"""
TOK_ESCURO = """--bg:#0B0F14; --surface:#121821; --surface-2:#161E29; --ink:#F3F4F6; --ink-2:#C3C9D1; --muted:#8B95A3; --line:#232C38; --line-2:#1B232E;
  --gold:#13D1D1; --gold-soft:#0F3436; --gold-ink:#5FE0E0; --graph:#18212D; --graph-ink:#F3F6F8; --on-acc:#04292A; --fs3:#0E8F8F; --tipbg:#1F2937;
  --s2:#E5E7EB; --s2-soft:#2A3340; --brass:#13D1D1; --brass-2:#8B95A3; --r:12px;
  --f-display:"Plus Jakarta Sans","Roboto",ui-sans-serif,system-ui,sans-serif; --f-text:"Plus Jakarta Sans","Roboto",ui-sans-serif,system-ui,sans-serif;
  --shadow:0 1px 2px rgba(0,0,0,.35),0 16px 36px -20px rgba(0,0,0,.75)"""
CORES = [  # cores fixas do acabamento da Taylor → Montreal
    ("rgba(149,140,88,", "rgba(19,209,209,"), ("rgba(181,172,119,", "rgba(95,224,224,"), ("rgba(244,241,232,", "rgba(243,246,248,"),
    ("rgba(7,44,33,", "rgba(17,24,39,"), ("#958C58", "#13D1D1"), ("#B5AC77", "#5FE0E0"), ("#D9D2A9", "#A7EEEE"), ("#D3CA94", "#7FE6E6"),
    ("#A89E66", "#13D1D1"), ("#E4E1D6", "#E5E7EB"), ("#F4F1E8", "#F3F6F8"), ("#EEEBE2", "#E5E7EB"), ("#072C21", "#1F2937"),
]
CSS_EXTRA = """
/* ===== Montreal Business: turquesa + grafite do site, Plus Jakarta Sans, cantos arredondados ===== */
.mk-mt{display:flex;align-items:center;gap:13px}
.mk-mt i{display:block}
.mk-mt .mtc{width:33px;height:37px;background:#13D1D1;-webkit-mask:url("data:image/png;base64,__ICO__") center/contain no-repeat;mask:url("data:image/png;base64,__ICO__") center/contain no-repeat}
.mk-mt .mtw{width:134px;height:25px;background:#F3F6F8;-webkit-mask:url("data:image/png;base64,__WRD__") center/contain no-repeat;mask:url("data:image/png;base64,__WRD__") center/contain no-repeat}
:root[data-client="ty"] .top{border-radius:18px;background:radial-gradient(120% 140% at 100% 0%,rgba(19,209,209,.10),transparent 46%),var(--graph)}
:root[data-client="ty"] .top::after{border-radius:12px}
:root[data-client="ty"] .brand-txt h1{letter-spacing:.2em;font-weight:700}
:root[data-client="ty"] .chip,:root[data-client="ty"] .chip[aria-pressed=true]{letter-spacing:.12em;font-size:11px}
:root[data-client="ty"] .presets>.pchips{gap:24px}
:root[data-client="ty"] .sh h2{font-weight:600;letter-spacing:-.01em}
:root[data-client="ty"] .tile .v,:root[data-client="ty"] .num{font-variant-numeric:tabular-nums}
@media (max-width:760px){:root[data-client="ty"] .top{border-radius:14px}}
"""
MARCA_TY = '<div class="mk-ty" role="img" aria-label="Taylor Imóveis"><i class="tyc"></i><i class="tyw"></i></div>'
MARCA_MT = '<div class="mk-mt" role="img" aria-label="Montreal Business"><i class="mtc"></i><i class="mtw"></i></div>'


def tx():
    t = json.loads(json.dumps(montar_meta.TX))
    for k in t:
        for par in t[k]:
            par[0] = par[0].replace(montar_meta.FONTE_META, FONTE_META).replace(montar_meta.FONTE_GADS, FONTE_GADS)
            par[1] = par[1].replace(montar_meta.FONTE_META, FONTE_META).replace(montar_meta.FONTE_GADS, FONTE_GADS)
    return t


def ler_meta(arquivos):
    vistos, linhas = set(), []
    for f in arquivos:
        for x in montar_meta.ler(f):
            d = x["date_start"]
            if d < "2026-01-01" or (d, x["id"]) in vistos:
                continue
            vistos.add((d, x["id"]))
            inv = float((x.get("amount_spent") or {}).get("value") or 0)
            imp = int(x.get("impressions") or 0)
            if imp == 0 and inv == 0:
                continue
            lead = int(x.get("lead") or 0)
            form = min(int(x.get("onsite_conversion_lead_grouped") or 0), lead)
            linhas.append((d, x.get("campaign_name") or "(sem nome)", x.get("adset_name") or "(sem nome)", x.get("name") or "(sem nome)",
                           round(inv * 100), imp, int(x.get("link_click") or 0), int(x.get("clicks") or 0), form, lead - form, lead))
    if not linhas:
        sys.exit("nenhuma linha de 2026 nas respostas da Meta")
    linhas.sort()
    idx = [{}, {}, {}]
    ix = lambda m, k: m.setdefault(k, len(m))
    r = [[(dt.date.fromisoformat(d) - montar.BASE).days, ix(idx[0], c), ix(idx[1], g), ix(idx[2], ad), *n] for d, c, g, ad, *n in linhas]
    ordem = lambda m: sorted(m, key=m.get)
    print(f"[Montreal · Meta] {len(r)} linhas · {linhas[0][0]} a {linhas[-1][0]} · {len(idx[0])} campanhas · "
          f"R$ {sum(z[4] for z in r)/100:,.2f} · leads {sum(z[10] for z in r)} (form. {sum(z[8] for z in r)}, site {sum(z[9] for z in r)})")
    return {"c": ordem(idx[0]), "g": ordem(idx[1]), "a": ordem(idx[2]), "r": r}, linhas[-1][0]


def identidade(html):
    lg = json.load(open(LOGO, encoding="utf-8"))
    i0, i1 = html.index("<style>", html.index("</head>")), html.index("</style>", html.index("</head>"))
    css = html[i0:i1]
    # tokens: claro, escuro (sistema) e escuro (forçado)
    css, n1 = re.subn(r':root\[data-client="ty"\]\{[^}]*\}', lambda m: ':root[data-client="ty"]{\n  ' + TOK_CLARO + "}", css, count=1)
    css, n2 = re.subn(r'(:root\[data-client="ty"\]:not\(\[data-theme="light"\]\)\{)[^}]*\}', lambda m: m.group(1) + "\n  " + TOK_ESCURO + "}", css, count=1)
    css, n3 = re.subn(r'(:root\[data-client="ty"\]\[data-theme="dark"\]\{)[^}]*\}', lambda m: m.group(1) + "\n  " + TOK_ESCURO + "}", css, count=1)
    if not (n1 and n2 and n3):
        sys.exit("[montreal] blocos de tokens da Taylor não encontrados no template")
    for a, b in CORES:
        css = css.replace(a, b).replace(a.lower(), b)
    # cantos: acabamento reto da Taylor → arredondado
    css = "\n".join(re.sub(r"border-radius:(2|3)px", lambda m: "border-radius:" + ("6" if m.group(1) == "2" else "8") + "px", ln)
                    if 'data-client="ty"' in ln else ln for ln in css.split("\n"))
    css += CSS_EXTRA.replace("__ICO__", lg["ico"]).replace("__WRD__", lg["wrd"])
    html = html[:i0] + css + html[i1:]
    html = re.sub(r"family=Josefin\+Sans:wght@[0-9;]+&family=Inter:wght@[0-9;]+", "family=Plus+Jakarta+Sans:wght@300;400;500;600;700", html)
    # restos do painel interno (escondidos) e comentários do código: fora da página do cliente
    html = re.sub(r'<option value="0">SH Prime</option>.*?<option value="3">Taylor</option>', "", html, count=1, flags=re.S)
    html = re.sub(r"Fonte: planilhas \[BaseData\][^<]*", "", html, count=1)
    html = re.sub(r"/\*[^*]*?(Taylor|taylor)[^*]*?\*/", "", html)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--ate")
    ap.add_argument("--gads")
    a = ap.parse_args()
    dm, ult = ler_meta(a.arquivos)
    if a.ate and ult < a.ate:
        print(f"AVISO: Meta só até {ult} (esperado {a.ate})")
    snap_g = None
    if a.gads:
        snap_g, ult_g, resumo = montar_gads.construir(a.gads)
        print(resumo.replace("Taylor", "Montreal"))
        os.makedirs(os.path.dirname(CACHE_G), exist_ok=True)
        json.dump(snap_g, open(CACHE_G, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    elif os.path.exists(CACHE_G):
        snap_g = json.load(open(CACHE_G, encoding="utf-8"))
        print("Google Ads: usando a última cópia em dados/montreal_gads.json")
    ga = json.load(open(CACHE_GA, encoding="utf-8")) if os.path.exists(CACHE_GA) else None
    nav = (montar_meta.NAV_O + (montar_meta.NAV_G if snap_g else "") + montar_meta.NAV_I.replace(' aria-pressed="true"', ' aria-pressed="false"')
           + (montar_meta.NAV_A if ga else "") + "</nav>")
    sem_site = [] if ga else [
        ("Meta, Google e site no mesmo período", "Meta e Google no mesmo período"),
        ("Meta Ads, Google Ads e site no mesmo período", "Meta Ads e Google Ads no mesmo período"),
        ("<h2>Plataformas e site</h2>", "<h2>Plataformas</h2>"),
        (" No site, as sessões e os contatos registrados pelo GA4.", ""),
        (", os leads que as plataformas registraram e o que aconteceu no site.", " e os leads que as plataformas registraram."),
        ("Fontes: Meta Ads e Google Ads (conectores oficiais) e Google Analytics 4 do site, somente 2026. Leads = leads da Meta + conversões do Google Ads. Contatos no site = WhatsApp, telefone e formulário registrados pelo GA4.",
         "Fontes: Meta Ads e Google Ads (conectores oficiais), somente 2026. Leads = leads da Meta + conversões do Google Ads."),
    ]
    trocas = [(montar_meta.PLANILHA_TY, ""), (MARCA_TY, MARCA_MT), ('name:"Taylor"', 'name:"Montreal Business"'), ('ty:"Taylor"', 'ty:"Montreal"'),
              ("com a Taylor no período", "com a Montreal no período")] + sem_site
    agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    montar.solo(agora, {"ty": dm}, "ty", PASTA, TITULO, fonte=FONTE_META, nav=nav, snap_g=snap_g, tx=tx(), ga=ga, trocas=trocas)
    p = os.path.join(montar.RAIZ, "docs", PASTA, "index.html")
    html = identidade(open(p, encoding="utf-8").read())
    resto = [w for w in ("Taylor", "taylor", "TAYLOR") if w in re.sub(r"<style>.*?</style>", "", html, flags=re.S)]
    if resto:
        print("AVISO: ainda há menções a", resto)
    open(p, "w", encoding="utf-8").write(html)
    print(f"docs/{PASTA}/index.html pronto ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
