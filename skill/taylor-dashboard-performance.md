---
name: taylor-dashboard-performance
description: Página de performance da Taylor Imóveis (performance.creativeimob.app/taylor/): Visão geral, Meta Ads, Google Ads e GA4 num link só. Use para qualquer ajuste, dado, validação, publicação ou caso pontual da Taylor.
---

# Taylor Imóveis · Dashboard de performance

Skill específica da Taylor. O que é comum a todos os clientes (painel interno, Cérebro, métricas, motor de gráficos, template único, rotina geral) está na skill geral `creativeimob-dashboard-performance`; leia as duas quando mexer no código. Casos pontuais da Taylor se tratam por aqui.

## O cliente
- **Taylor Imóveis** (taylorimoveis.com): imobiliária de alto padrão em SP (Jardim Europa, Jardim América, Jardim Paulista, Itaim Bibi, Alto de Pinheiros, Alto da Boa Vista, Cerqueira César, Paraíso). Venda e locação de imóveis de terceiros, campanhas por bairro e tipo (casas, apartamentos, coberturas).
- Cliente da CreativeImob. Quem pede: **Paulo** (Data & BI, paulo@creativeimob.com). Português do Brasil, frases curtas; o padrão exigido é "extremamente elegante", "muito sênior".
- A página é **entregue ao cliente**: só dados da Taylor no código, identidade visual da Taylor, sem Cérebro e sem abas de outros clientes. Site público, sem senha (decisão do Paulo).

## Onde está
- **Link único**: https://performance.creativeimob.app/taylor/ (`docs/taylor/index.html`; `/taylor/google/` só redireciona para a aba Google). Repositório público `paulollaque12/creativeimob-performance-midia`, branch `main`, GitHub Pages em `/docs`.
- Gerada por `tools/montar_meta.py` → `montar.solo(agora, dados, "ty", "taylor", "Taylor Imóveis · Performance Meta Ads", fonte=FONTE_META, nav=…, snap_g=…, tx=TX, ga=…, trocas=[(PLANILHA_TY,"")])`, a partir do mesmo `fonte/template.html` do painel interno (o acabamento da Taylor vive no CSS `:root[data-client="ty"] …`).
- Arquivos da Taylor: `tools/montar_meta.py` (Meta + montagem; `CONTA`, `PLANILHA_TY`, `FONTE_META`, `FONTE_GADS`, `NAV_O/NAV_I/NAV_G/NAV_A`, mapa `TX`), `tools/montar_gads.py` (Google Ads), `tools/ga4.py` (GA4), `dados/taylor_gads.json` (cópia do Google), `dados/ga4.json` (cópia do GA4), `ATUALIZAR.md` (seções "Página só da Taylor", "Taylor · aba Google Ads", "Taylor · GA4", "Taylor · Visão geral").
- No painel interno (`performance.creativeimob.app/`) a Taylor também é uma aba (planilha `[TAYLOR] report semanal`), com o mesmo visual; lá não há Google Ads, GA4 nem Visão geral.
- Acesso ao repo no sandbox: `add_repo` (owner `paulollaque12`, repo `creativeimob-performance-midia`, access `push`) + `git clone --depth 1` + `register_repo_root`. Antes de push: `git pull --rebase` (outras sessões e a tarefa diária também publicam). Deploy: `gh api repos/paulollaque12/creativeimob-performance-midia/actions/runs?per_page=1` com "completed success" e o sha do commit. Cache: Ctrl+Shift+R (o Paulo às vezes manda print da versão antiga).

## Estrutura da página (topo → baixo)
- **Cabeçalho** (decisões de 08/11): marca Taylor (brasão + "TAYLOR IMÓVEIS") | título = **só o nome da ferramenta** em uma linha + frase curta (`PLT`/`platTitle()`): Visão geral "Meta, Google e site no mesmo período" · Meta Ads "Entrega, custo e leads na Meta" · Google Ads "Entrega, custo e conversões no Google" · GA4 "Visitas e contatos no site"; símbolo da plataforma ao lado do título (∞ Meta, G Google, barras GA4, grade Visão geral). À direita, **seletor de plataforma em caixa** `Overview | Google Ads | Meta Ads | GA4` (ordem e nome "Overview" pedidos em 08/11) (`.plat`, escolha salva em `cimob-plat`, abre em Visão geral) e o botão de tema. Embaixo: fio dourado; datas (+ Campanha em Meta/Google); períodos rápidos (Mês atual, Últimos 7 dias, Últimos 30 dias, Mês anterior, Ano até ontem) e "Atualizado em…".
  - RECUSADO pelo Paulo: abas de plataforma sublinhadas embaixo da marca com datas à direita ("tinha gostado da versão anterior"); títulos longos ("Performance de mídia · Meta Ads") que quebravam linha.
  - 761–1279px: chips com gap 22px; 761–1023px: plataformas descem para baixo da marca e o "Atualizado" vai para a última linha; ≤760px: botões de plataforma na caixa segmentada de largura total.
- **Overview** (antes "Visão geral"; `data-p="o"`, `main#mainOv`, `showOv()/renderOv()`; inspirada na aba Overview do Looker da Taylor): Big numbers (Investimento, Sessões no site, Cliques, Leads, Custo por lead, Contatos no site + faixa Impressões, CPM, CPC, Verba Meta · Google) → Plataformas e site (cartões Meta Ads | Google Ads | Site · GA4 com número principal e Volume / Custo / Taxas) → **Desempenho dos últimos três meses** (só 3 meses, pedido do Paulo; barras de investimento Meta `--gold` e Google `--brass-2` largas com valor na base, linha Leads somados) → Últimos três meses (tabela: Total, Meta, Google, Site; "Últ. × ant. · parcial" com mês corrente incompleto). Leads = leads Meta + conversões Google.
- **Meta Ads** e **Google Ads**: modelo da página de cliente (Insights → Resumo → Funil → Mensal → Diária → Indicadores diários → Detalhes). Google acrescenta nível **Palavra-chave** e coluna **IS sup.** Textos trocados por plataforma em tempo real pelo mapa `TX` (`i18n()`); na Meta "WhatsApp" vira "Site".
- **GA4** (`data-p="a"`, `main#mainGa`): ver seção GA4 abaixo.

## Identidade visual (padrão "cliente"; não reverter)
- Cores do site: verde `#072C21`, dourado `#958C58`, cinza `#707070`, borda `#D8D8D8`. Tokens Taylor: barras `#1E5A43`, cabeçalho `#0E2C22`/`#15382B`, latão `--brass #958C58`/`#B5AC77`, `--brass-2`, fundo marfim `#F2F1EC`. **Noite é o padrão da página** (sem `shp-theme` salvo abre escuro): barras douradas `#A89E66`, linha marfim `#E4E1D6`, funil dourado → oliva → verde `#17573F`. Dia: barras verde, linha dourada.
- Fontes: títulos **Josefin Sans** (caixa alta espaçada), texto e números **Inter**; cantos retos (`--r:6px`, campos 3px).
- Cabeçalho em grade alinhada, moldura dourada fina, fio dourado em degradê, campos de 50px com ícone de traço dourado e rótulo dourado em caixa alta, períodos como abas em caixa alta com traço dourado na ativa.
- Seções numeradas (fio dourado + "01", "02"…), títulos 22px peso 500, textos sem quebra (`.bi{max-width:none}`).
- Big numbers com ícone dourado de traço fino por posição (`--ico` por `nth-child`: $, olho, cursor, pessoa, etiqueta, alvo), número Inter 400; "Comparação: …" abaixo dos big numbers.
- Botões segmentados iguais (32px, 9,5px, caixa alta, ativo verde sólido).
- **Tabelas**: dimensão travada à esquerda numa linha só com "…" (nome no `title`), métricas com **largura padrão e centralizadas**, linhas 46px, cabeçalho e total fixos, rolagem **fina dourada translúcida**. Detalhes: 440px de altura, nome 300px, volume 112px, custos/taxas 92px. GA4: largura 100% (mín. 940px), métricas 96px, máx. 460px; eventos sem rolagem lateral.
- Tooltip ao lado do cursor. Conferir com as fontes reais no navegador do app (o Playwright do sandbox bloqueia Google Fonts).

## Fonte 1 · Meta Ads (conector oficial)
- Conta **[CI] taylor imóveis 2.0** `3063928683998040`. Gasto desde **11/04/2026**.
- `mcp__Meta_Ads__ads_get_ad_entities`, **um mês por chamada** (o período inteiro dá Bad Gateway), de 2026-04 até ONTEM: `level=ad`, `time_increment="1"`, `time_range` do mês, `fields=[id,name,campaign_name,adset_name,amount_spent,impressions,clicks,link_click,lead,onsite_conversion_lead_grouped]`, `filtering=[impressions GREATER_THAN 0]`, `limit=1000`, `reporting_purpose=["metric_lookup"]`, `include_additional_context=false` (na tarefa: `scheduled_task_run true`, `advertiser_job report_measure_or_look_up`). Resposta em `/tmp/meta/AAAA-MM.json` (inline: gravar o JSON; `next_cursor` → `AAAA-MM-2.json`). Não chamar `offer_report`.
- Regras: Investimento = `amount_spent`; Cliques no link = `link_click`; **Leads = `lead`** (formulário + site/pixel); Formulário = `onsite_conversion_lead_grouped`; **Site = lead − formulário** (ocupa o campo "WhatsApp", rótulos trocados para "Site"/"Leads do site"). O conector não traz conversas de WhatsApp (os leads de WhatsApp da planilha não entram: ex. ago/26 Meta 82 × planilha 145).
- Conferência (até 05/11/2026): 2.387 linhas, 13 campanhas, R$ 42.160,87, 923 leads (698 formulário, 225 site); investimento, impressões e cliques iguais à planilha de mai–nov (planilha só desde 27/04: abril Meta R$ 5.094,72 × planilha R$ 1.245,94).

## Fonte 2 · Google Ads (conector Google Ads)
- Conta Taylor `5451475929`, `login_customer_id=4498709696` (MCC CREATIVEIMOB). Só `mcp__Google_Ads__search_search` (o servidor tem ferramentas de escrita: nunca usar sem pedido).
- Sete consultas de 2026-01-01 até ONTEM (`limit` 10000) em `/tmp/gads/`: `ads`, `camp`, `adinfo`, `kw`, `conv_ad`, `conv_camp`, `conv_kw` (campos exatos no cabeçalho de `tools/montar_gads.py`; as de conversão costumam vir inline). Montagem junto com a Meta: `python3 tools/montar_meta.py --gads /tmp/gads --ate ONTEM /tmp/meta/*.json` (sem `--gads` reaproveita `dados/taylor_gads.json`).
- Regras (Paulo, iguais ao Looker): Cliques = clicks; CTR = cliques ÷ impressões; **Leads = conversões do Google Ads (todas as ações)**; Formulário × WhatsApp pela ação ("whats"/"zap" = WhatsApp; "Rota" só no total); Performance Max = linha "(Performance Max · sem detalhe por anúncio)"; IS sup. = Σ impressões no topo ÷ Σ elegíveis. Modelo `{c,g,a,k,r,kr}`; `kr` = `[dia,iC,iG,iK,inv,imp,clk,clk,form,whats,leads,topImp,eligTop]`.
- Conferência (08/11/2026): 01–07/11 R$ 1.287,49, 3.764 impressões (−65,6%), 511 cliques (+114,7%), CTR 13,58%, 0 conversões = PDF do Looker. 2026 até 07/11: R$ 46.152,45, 31.392 cliques, 107 conversões (jan 74, fev 0, mar 5, abr 6, mai 6, jun 4, jul 2, ago 8, set 1, out 1), 157 palavras-chave.
- Diagnóstico entregue: ações de conversão ativas sem disparo desde set/26; o Google Ads importa `agendar_visita` e `quero_mais_informacoes` (sem disparos), não os eventos que o site usa.

## Fonte 3 · GA4 (conector Google Analytics)
- **Decisão do Paulo: GA4 só da Taylor** (botão na página dela; não entra no painel interno nem no artefato). Propriedade **Taylor Brasil GA4** `330078762` (vinculada ao Google Ads). Conector personalizado "Google Analytics" (detalhes no doc do projeto `claude/mcp_ga4.md`).
- `python3 tools/ga4.py --consultas --ate ONTEM` imprime **5 pedidos** (`cube`, `lp`, `ev`, `utm`, `ct`); cada um vai a `mcp__Google_Analytics__run_report` e a resposta para `/tmp/ga/ty_<q>.json` (vêm em arquivo; `limit` "100000"). Depois `python3 tools/ga4.py --pasta /tmp/ga --ate ONTEM` → `dados/ga4.json` (~400 KB; só avisa se o GA4 parar). `montar_meta.py` lê o arquivo e passa `ga=` (marcador `/*__GA4__*/null`).
  - `cube`: date × canal × origem/mídia × campanha × dispositivo → sessions, engagedSessions, newUsers, screenPageViews, userEngagementDuration.
  - `lp`: date × landingPage (sessions ≥ 3/dia) → sessions, engagedSessions, newUsers; fora das 300 maiores vira "/<pasta>/… (demais páginas)"; o resto do dia = "Demais páginas".
  - `ev`: date × eventName → eventCount, keyEvents.
  - `utm`: date × sessionSource × sessionMedium × sessionCampaignName × sessionManualAdContent (= `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`) → sessions, engagedSessions, newUsers, userEngagementDuration.
  - `ct`: eventos de contato × canal × origem/mídia × campanha × dispositivo × landingPage × utm_content → eventCount.
- **Contatos** = regex `.*whatsapp.*|cabecalho-telefone|phone_site|.*-form|fale_conosco|agendar_visita|generate_lead|cadastre_seu_imovel`. Tipo pelo nome: whats → WhatsApp; phone/telefone/ligacao → Telefone; avalie/anuncie/cadastre → Captação de imóvel; resto Formulário. Eventos ativos hoje: `imovel-whatsapp-form`, `cabecalho-whatsapp`, `btn_flutuante-whatsapp-form`, `imovel-fale_conosco-form`, `rodape-contato-form`, `imovel-informacoes-form`, `imovel-solicitar_ligacao-form`, `cabecalho-telefone`; os key events (`whatsapp_flutuante`, `generate_lead`, `whatsapp_site`, `agendar_visita`, `phone_site`) só dispararam em jan/26 (tags antigas). Outros: page_view, view_item, retencao_30s/60s, rota, rodape-email.
- **Origem consolidada** (leitura da CreativeImob): Meta Ads (anúncios) = fonte facebook/instagram/ig/fb/meta (ou campanha com ID 120…) + mídia paga ou campanha `_meta_`/catalogo; Meta orgânico (perfis e links); Google Ads; Busca orgânica; Direto; Assistentes de IA; Links de WhatsApp; Sites e portais; Outras redes; Sem origem identificada; E-mail; Outras pagas.
- **Tipos de página**: Home, Página de imóvel (`/imovel/…` e slugs `/apartamento-com-3-quartos-…`, `/casa-…`), Lançamentos e condomínios, Busca e listagem (`/imoveis/venda/…`), Contato e captação, Institucional, Conteúdo e blog, Landing page de anúncio, Sem página registrada, Outras páginas.
- Blocos da aba GA4: alerta de coleta parada → **Leituras do site** (wins/lows) → **Resumo do site** (Sessões, Novos usuários, Taxa de engajamento, Contatos no site, Taxa de contato, Tempo médio engajado + faixa) → **Funil do site** (esquerda: sessões → engajadas → contatos + faixa "Do anúncio da Meta ao site": Cliques Meta, Sessões Meta, Contatos, Custo/contato; direita: Tipo de contato + De onde vêm os contatos) → Evolução mensal (sessões + Contatos | Taxa de contato | Engajamento) → Evolução diária → **De onde vêm as visitas** (faixa "Links com UTM" no topo + tabela Consolidada | Canal GA4 | Origem / mídia | Campanha | Conteúdo | Dispositivo) → **Páginas de destino** por tipo com "+" → **Eventos** (contatos × demais, "parou").
  - RECUSADO: bloco de UTM grande embaixo do funil ("feio"); a versão que deixava espaço vazio nos cartões.
- Leituras do site (`gInsights`) usam o mesmo cartão dos Insights da Meta/Google (ícone ↗/↘, título, selo com o número, frase): `add(arr,peso,tipo,html,selo)`; o título é o `<b>…</b>` do html e o resto vira a frase.
- Big numbers do GA4 com ícones próprios (`#gTiles .tile:nth-child(n)`: tela, pessoa +, pulso, balão, %, relógio).
- Leituras do site (`gInsights`): Δ de sessões/contatos/taxa de contato/engajamento/tempo (≥8%); origem que mais converte (≥100 sessões, ≥3 contatos, ≥1,3× a média); origem que mais cresceu/caiu (±25%); "X% das sessões sem origem" (≥15%); Meta sem UTM (sessões de anúncio Meta ÷ cliques no link < 40%); entrada que mais converte; página com muita entrada e pouco engajamento (≥5% das sessões, <35%); evento de contato que parou; pico atípico (≥3× a mediana com engajamento baixo); GA4 sem coleta.

## Números e achados já apresentados
- Meta 01–14/10: R$ 2.279,03, 31 leads, CPL R$ 73,52 (−6,9%), CPM +135%, CPC +124%; venda Alto da Boa Vista a mais eficiente (R$ 48,87); locação a que mais perdeu leads.
- Visão geral 01–07/11/2026: R$ 1.601,45 investidos (80% Google), 2.293 sessões, 11 leads, CPL R$ 145,59, 16 contatos no site. Set–out: Google R$ 4,5–4,8 mil/mês para 1 conversão/mês; Meta 70–121 leads/mês (CPL R$ 46–65).
- GA4 01–07/11: 2.293 sessões, 16 contatos (0,70%), 15 por WhatsApp; busca orgânica 7 contatos (2,98%); **40% das sessões sem origem** (Unassigned); **nenhuma visita da Meta chega com UTM desde 01/10** (0 sessões de anúncio Meta para 111 cliques no link); só 37 sessões com UTM, todas do Google Ads (92% com os 4 parâmetros); Paid Search só 34 sessões para 511 cliques do Google. 2026: 122.237 sessões, 727 contatos; pico de ~38 mil sessões em mar/26 (provável robô).
- Recomendações feitas ao Paulo: UTM nos anúncios da Meta (`utm_campaign`, `utm_source`, `utm_medium`, `utm_content` com o nome do anúncio); revisar auto-tagging/consentimento do Google; marcar os eventos de contato do site como key events e importar os mesmos no Google Ads.

## Rotina diária (tarefa agendada)
- "Atualizar painel de mídia CreativeImob" (`trig_018dybxSCkNo5bxAbZ7F7Exq`, 07:51 America/Sao_Paulo, aprovação automática, push). Passo **3b** = Taylor: Meta (um mês por chamada) → Google (7 consultas) → GA4 (5 consultas + `ga4.py --pasta`) → `montar_meta.py --gads /tmp/gads --ate ONTEM /tmp/meta/*.json`; commit de `docs/taylor/index.html`, `dados/taylor_gads.json`, `dados/ga4.json`. Sem Meta: pula a Taylor; sem Google ou GA4: reaproveita a última cópia e avisa.
- Meta Ads, Google Ads e Google Analytics são conectores personalizados e não aparecem na lista de conectores da tarefa: se a execução avisar que faltam, o Paulo precisa ativá-los nas configurações da tarefa. Pendente: confirmar na execução de 09/11/2026 que o GA4 entrou.
- Ao mudar consultas ou passos da Taylor, atualizar o prompt da tarefa (`update_trigger`), `ATUALIZAR.md` e esta skill.

## Como trabalhar na Taylor
1. Clonar/atualizar o repo. Para reconstruir só a página sem rebuscar a Meta, extrair o snapshot atual: ler `docs/taylor/index.html` do último commit, achar `\n  ty:{` → `snap:` e fazer `json.JSONDecoder().raw_decode`; depois chamar `montar.solo(...)` com `snap_g=json.load(open('dados/taylor_gads.json'))`, `ga=json.load(open('dados/ga4.json'))`, `nav=NAV_O + NAV_I(sem aria-pressed=true) + NAV_G + NAV_A + "</nav>"`, `tx=TX`, `trocas=[(PLANILHA_TY,"")]`.
2. Editar `fonte/template.html` (CSS da Taylor em `:root[data-client="ty"] …`; abas em `setPlat`, `showOv`, `renderGa`). Depois reconstruir também o painel interno (`tools/montar.py … --ate ONTEM`), que usa o mesmo template.
3. Testar: `node --check` no `<script>` de `docs/taylor/index.html`; Playwright (bloquear `**/fonts.*/**`; `localStorage` `cimob-plat` = o/m/g/a e `shp-theme`), 1360 escuro e claro, 1100, 820 e 400; `scrollWidth` igual à janela; `pageerror` vazio; clicar nas 4 abas e conferir os `main` visíveis; olhar o print.
4. Commit (`git -c user.name="Claude" -c user.email="noreply@anthropic.com"`, fim com `Co-Authored-By` e `Claude-Session`), `git pull --rebase`, push, conferir o deploy.
5. Responder curto, com o que mudou e os números.

## Armadilhas da Taylor
- Novos `.seg` NÃO podem ficar dentro de `.tbar .seg` (o listener do nível da tabela pega todos).
- Ao inserir um `<main>`, conferir que o `</main>` anterior não foi engolido (o GA4 já ficou escondido dentro do `mainCer`).
- `pct(v,0)` não existe (só 1 ou 2 casas): usar `pc0`.
- `SNAP_G`/`TXD` são definidos depois do primeiro `showClient`: código da Visão geral fica antes de `setPlat`, não no boot.
- Os ícones dos big numbers seguem a posição (`nth-child`), então a ordem dos tiles importa.
- Nada de outras imobiliárias no código da página (o `solo` limpa planilhas e abas; `tools/ga4.py` só tem `ty`).
- Só agregados; nunca dados pessoais de leads.
