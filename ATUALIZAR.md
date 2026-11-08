# Rotina de atualização

Roda sozinha todo dia às 07:51 (America/Sao_Paulo) pela tarefa agendada "Atualizar painel de mídia CreativeImob" (trig_018dybxSCkNo5bxAbZ7F7Exq).

Objetivo: deixar `docs/index.html` com os dados até ontem (D-1) e publicar. Em qualquer falha, **parar sem publicar**.

1. Clonar o repositório (`git clone --depth 1 https://github.com/paulollaque12/creativeimob-performance-midia`).
2. Ler as quatro planilhas com o conector **Google Sheets** (`get_values`):
   - SH Prime: `spreadsheetId=1tSgEdMFQKXgaRf-LxNuDTUfHIM3pTlhiJ-NF15bBSps`, `range=Meta!A1:Q40000`
   - Nova SP: `spreadsheetId=1cbrG6udFXUzYvpxEVb6m0ru8A0oD_DUgeEMn5ZsRpUo`, `range=Meta!A1:Q40000`
   - Lopes Prime: `spreadsheetId=16eTUPB8t0bBBroTn3kQyVqq6SrRsajPMK0DMwkILG6Y`, `range=Meta!A1:Q40000`
   - Taylor: `spreadsheetId=1iNZ5W8qUInPaw87_hG-nLwlB1pNubzW32PsfUi0qnTM`, `range='[BASE] meta'!A1:R40000`
   O resultado é grande e o conector salva em arquivo: usar o caminho do arquivo, nunca colar o conteúdo na conversa.
3. Montar: `python3 tools/montar.py --sh <arquivo_sh> --nsp <arquivo_nsp> --lp <arquivo_lp> --ty <arquivo_ty> --ate <ontem AAAA-MM-DD>`.
   O script falha se o cabeçalho mudar, se não houver linhas de 2026 ou se alguma das quatro bases não chegar até ontem.
4. Conferir a saída (linhas, última data, investimento e leads de cada cliente).
5. Commitar só `docs/index.html` com a mensagem `Atualiza dados até DD/MM/AAAA` e dar push na `main`.
6. Responder em uma linha: última data de cada cliente, investimento e leads do mês, link do site.

Mudanças de layout ou de regra: editar `fonte/template.html` (e republicar o artefato do Claude com o mesmo arquivo), rodar o passo 3 e commitar `fonte/` + `docs/`.

## Página só da Taylor, direto da Meta (performance.creativeimob.app/taylor/)
Criada em 06/11/2026. Não usa a planilha: lê o conector **Meta Ads** (conta [CI] taylor imóveis 2.0, `3063928683998040`).
1. `mcp__Meta_Ads__ads_get_ad_entities`, **um mês por chamada** (o período inteiro dá Bad Gateway), de 2026-04-01 até ontem:
   `level=ad`, `time_increment="1"`, `time_range={"since":…,"until":…}`,
   `fields=[id,name,campaign_name,adset_name,amount_spent,impressions,clicks,link_click,lead,onsite_conversion_lead_grouped]`,
   `filtering=[{"field":"impressions","operator":"GREATER_THAN","value":["0"]}]`, `limit=1000`, `reporting_purpose=["metric_lookup"]`, `include_additional_context=false`.
   Cada resposta vai para arquivo: copiar para `/tmp/meta/AAAA-MM.json`. Se vier `pagination.next_cursor`, buscar a próxima página e salvar como `AAAA-MM-2.json`.
2. `python3 tools/montar_meta.py --ate <ontem> /tmp/meta/*.json` → gera `docs/taylor/index.html`.
3. Commit de `docs/taylor/index.html`.
Regras: Leads = `lead` da Meta (formulário + site/pixel); Formulário = `onsite_conversion_lead_grouped`; Site = diferença (rótulo "Site" no lugar de "WhatsApp"). O conector não traz conversas de WhatsApp, então os leads de WhatsApp da planilha não entram nessa página.

## Taylor · aba Google Ads (mesmo endereço performance.creativeimob.app/taylor/, filtro Meta Ads | Google Ads no topo)
Desde 08/11/2026 a página da Taylor tem as duas plataformas no mesmo link: botões **Meta Ads | Google Ads** no cabeçalho trocam os dados na hora (a escolha fica salva no navegador, chave `cimob-plat`). `/taylor/google/` só redireciona para `/taylor/` já na aba Google.
Fonte do Google: conector **Google Ads** (conta Taylor `5451475929`, `login_customer_id=4498709696`). Mesmo formato da Meta + nível **Palavra-chave** e coluna **IS sup.** na tabela.
1. Sete consultas `mcp__Google_Ads__search_search` de `2026-01-01` até ONTEM (`limit` 10000), cada resposta salva em `/tmp/gads/<nome>.json` (as grandes vêm em arquivo; as de conversão costumam vir inline: gravar o JSON da resposta no arquivo). Campos exatos no cabeçalho de `tools/montar_gads.py`: `ads`, `camp`, `adinfo`, `kw`, `conv_ad`, `conv_camp`, `conv_kw`.
2. Uma montagem só, junto com a Meta: `python3 tools/montar_meta.py --gads /tmp/gads --ate ONTEM /tmp/meta/*.json` → `docs/taylor/index.html` e `dados/taylor_gads.json` (cópia dos dados do Google). Sem `--gads`, reaproveita `dados/taylor_gads.json`.
Regras do Google: Cliques = clicks (CTR = cliques ÷ impressões, como no Looker); **Leads = conversões do Google Ads (todas as ações)**, como no Looker; a origem separa Formulário × WhatsApp (ação com "whats"/"zap" = WhatsApp; "Rota" fica só no total); Performance Max entra como "(Performance Max · sem detalhe por anúncio)"; IS sup. = Σ impressões no topo ÷ Σ elegíveis (das palavras-chave). Os textos que mudam por plataforma ficam no mapa `TX` de `tools/montar_meta.py` (troca em tempo real, sem recarregar).
Conferência (08/11/2026): 01–07/11 R$ 1.287,49, 3.764 impressões (−65,6%), 511 cliques (+114,7%), CTR 13,58% (+523,6%), 0 leads = PDF do Looker. 2026 até 07/11: R$ 46.152,45, 31.392 cliques, 107 conversões (jan 74, fev 0, mar 5, abr 6, mai 6, jun 4, jul 2, ago 8, set 1, out 1 = Looker).

## Taylor · GA4 (mesmo endereço performance.creativeimob.app/taylor/, terceiro botão no topo: Meta Ads | Google Ads | GA4)
Desde 08/11/2026. Decisão do Paulo: GA4 **só na página da Taylor** (não entra no painel interno). Fonte: conector **Google Analytics** (`run_report`), propriedade `330078762`.
1. `python3 tools/ga4.py --consultas --ate ONTEM` imprime os CINCO pedidos exatos (`cube`, `lp`, `ev`, `utm`, `ct`). Fazer cada chamada `mcp__Google_Analytics__run_report` e salvar a resposta em `/tmp/ga/ty_<consulta>.json` (as grandes vêm em arquivo: copiar).
2. `python3 tools/ga4.py --pasta /tmp/ga --ate ONTEM` → `dados/ga4.json` (avisa se o GA4 parou; não falha).
3. A montagem da Taylor (`tools/montar_meta.py`) lê `dados/ga4.json` e acrescenta o botão GA4. Commit de `dados/ga4.json` junto com `docs/taylor/index.html`. Sem o conector Google Analytics na execução: pular e reaproveitar a última cópia.
Regras: Contatos = eventos de WhatsApp, telefone e formulário do site (regex em `tools/ga4.py`); "Origem consolidada" junta origem/mídia/campanha (anúncio Meta, perfis Meta, Google Ads, orgânica, direto, IA, sem origem). Páginas fora das 300 maiores viram grupos "(demais páginas)". `utm` = utm_source/medium/campaign/content (bloco "Links parametrizados" e visão "Conteúdo"). Tabelas do GA4 com coluna da dimensão travada e cabeçalho/total fixos.
Achados de 08/11/2026: 40% das sessões da Taylor chegam sem origem (Unassigned); quase nenhuma sessão é reconhecida como anúncio da Meta (falta UTM nos anúncios); pico de 38 mil sessões em março (provável robô). Nova SP (300839307) parou de coletar em 16/10/2026 e a Lopes trocou os eventos de contato em outubro (avisar o Paulo se ele pedir os outros sites).
