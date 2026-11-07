#!/usr/bin/env python3
"""Monta docs/taylor/index.html (performance.creativeimob.app/taylor/) direto do conector Meta Ads.

Uso:
  python3 tools/montar_meta.py [--ate AAAA-MM-DD] /tmp/meta/*.json

Cada <json> é a resposta salva de mcp__Meta_Ads__ads_get_ad_entities para a conta
[CI] taylor imóveis 2.0 (3063928683998040), com:
  level=ad, time_increment="1", um mês por chamada (time_range since/until),
  fields=[id, name, campaign_name, adset_name, amount_spent, impressions, clicks,
          link_click, lead, onsite_conversion_lead_grouped],
  filtering=[impressions GREATER_THAN 0], limit=1000, include_additional_context=false.

Regras da página da Taylor (fonte Meta, não a planilha):
- Leads = `lead` da Meta (formulário instantâneo + leads do site/pixel);
- Formulário = `onsite_conversion_lead_grouped`; Site = lead − formulário (o painel geral chama esse
  campo de WhatsApp; aqui ele é rotulado "Site"). A Meta não expõe conversas de WhatsApp pelo conector.
- Cliques = `link_click`; linhas com 0 impressões e 0 gasto são descartadas; só 2026.
"""
import argparse, datetime as dt, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar  # noqa: E402

CONTA = "3063928683998040"
PLANILHA_TY = "1iNZ5W8qUInPaw87_hG-nLwlB1pNubzW32PsfUi0qnTM"


def ler(caminho):
    o = json.load(open(caminho, encoding="utf-8"))
    if isinstance(o, list):
        o = json.loads(o[0]["text"])
    e = o["ad_entities"]
    return json.loads(e) if isinstance(e, str) else e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--ate", help="último dia esperado (AAAA-MM-DD); falha se a Meta não chegar até ele")
    a = ap.parse_args()
    vistos, linhas = set(), []
    for f in a.arquivos:
        for x in ler(f):
            d = x["date_start"]
            chave = (d, x["id"])
            if d < "2026-01-01" or chave in vistos:
                continue
            vistos.add(chave)
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
    def ix(m, k):
        if k not in m:
            m[k] = len(m)
        return m[k]
    r = [[(dt.date.fromisoformat(d) - montar.BASE).days, ix(idx[0], c), ix(idx[1], g), ix(idx[2], ad), *nums] for d, c, g, ad, *nums in linhas]
    ult = linhas[-1][0]
    if a.ate and ult < a.ate:
        sys.exit(f"Meta só até {ult} (esperado {a.ate}). Nada foi gerado.")
    ordem = lambda m: sorted(m, key=m.get)
    dados = {"ty": {"c": ordem(idx[0]), "g": ordem(idx[1]), "a": ordem(idx[2]), "r": r}}
    print(f"[Taylor · Meta] {len(r)} linhas · {linhas[0][0]} a {ult} · {len(idx[0])} campanhas · "
          f"R$ {sum(z[4] for z in r)/100:,.2f} · leads {sum(z[10] for z in r)} (form. {sum(z[8] for z in r)}, site {sum(z[9] for z in r)})")
    agora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    montar.solo(agora, dados, "ty", "taylor", "Taylor Imóveis · Performance Meta Ads",
                fonte="Fonte: Meta Ads, conta [CI] taylor imóveis 2.0 (leitura direta do conector oficial da Meta)",
                trocas=[(PLANILHA_TY, ""), ("formulário e WhatsApp", "formulário e site"),
                        ("as conversas por WhatsApp.", "os leads do site (pixel), como a Meta atribui."),
                        ("Leads por WhatsApp</h3><p class=\"bi\">Conversas iniciadas pelo botão de mensagem.",
                         "Leads do site</h3><p class=\"bi\">Cadastros no site atribuídos aos anúncios pelo pixel da Meta."),
                        ("WhatsApp", "Site"), ('["Tx. conv. (lead ÷ impressão)"', '["Tx. de conversão"')])


if __name__ == "__main__":
    main()
