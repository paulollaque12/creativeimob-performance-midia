---
name: dupllex-dashboard-performance
description: Página de performance da Dupllex Imóveis (performance.creativeimob.app/dupllex/): Overview, Google Ads, Meta Ads (provisória pela planilha) e GA4 num link só. Use para qualquer ajuste, dado, validação ou publicação da Dupllex.
---

# Dupllex · Dashboard de performance

Skill específica da Dupllex. O que é comum (template único, métricas, motor de gráficos, painel interno) está na skill mãe `creativeimob-dashboard-performance`; a página reaproveita a estrutura da Taylor (`taylor-dashboard-performance`) e o jeito de trocar identidade da Montreal (`montreal-dashboard-performance`).

## O cliente
- **Dupllex Imóveis** (dupllex.com.br): coberturas e imóveis de alto padrão em SP (Itaim Bibi, Jardins, Jardim Paulista). Campanhas por imóvel: Fernandes 51 (Itaim), Caçapava 83, Oscar 264, Maria Lisboa 1370, Mena Barreto 477, Sarutaiá 320, "coberturas".
- Quem pede: **Paulo** (Data & BI, paulo@creativeimob.com). Escreve em português ou espanhol: responder no idioma da mensagem.
- Página entregue ao cliente: só dados da Dupllex, identidade da Dupllex, sem Cérebro, sem nomes de outros clientes. Site público, sem senha.

## Onde está
- **Link**: https://performance.creativeimob.app/dupllex/ (`docs/dupllex/index.html`), repo `paulollaque12/creativeimob-performance-midia`, branch `main`, Pages em `/docs`. Criada em 17/11/2026.
- Gerador: `python3 tools/montar_dupllex.py [--meta /tmp/dx/meta/planilha.json] [--gads /tmp/dx/gads] [--ga /tmp/dx/ga] --ate ONTEM`. Sem uma opção, reaproveita a cópia: `dados/dupllex_meta.json`, `dados/dupllex_gads.json`, `dados/dupllex_ga4.json`.
- Logo: `fonte/dupllex_logo.json` (máscara PNG base64 do logo enviado em 17/11/2026, wordmark "dupllex" em branco `#FAFAFA` no cabeçalho, 104×38).
- Acesso ao repo: `add_repo` (push) + `git clone --depth 1` + `register_repo_root`. Antes do push: `git checkout -- tools/__pycache__` e `git pull --rebase` (outras sessões mexem no repo). Deploy: `gh api repos/paulollaque12/creativeimob-performance-midia/actions/runs?per_page=1` com o sha do commit.

## Como a página é feita
- `montar.solo(..., "ty", "dupllex", ...)` com a chave `ty` do template (Overview, Meta, Google, GA4, acabamento da Taylor). `identidade()` troca só no arquivo gerado: os 3 blocos de tokens `:root[data-client="ty"]`, as cores fixas do acabamento (`CORES`), a fonte (Josefin+Inter → **Archivo** `wdth,wght@100..125,200..700`), a marca e `CSS_EXTRA`.
- Botões: **Overview | Google Ads | Meta Ads | GA4** (mesma ordem da Taylor). Sem dados da Meta o script tira o botão Meta e troca textos (`sem_meta`); com Meta usa `com_meta`.
- Template preparado para página sem Meta (17/11/2026, vale para todos): `ovMod` ignora modelo Meta vazio; faixa "Verba Meta · Google" vira "Tx. conv." com uma plataforma só; meses da Overview entram também se tiverem sessões; `setPlat` cai em "o" se não houver botão Meta; `setModel` aceita modelo vazio.
- Conferir sempre: `grep -c Taylor docs/dupllex/index.html` fora do CSS = 0 (o script avisa).

## Identidade visual (do site; não reverter sem pedido)
- Site monocromático: grafite `#212121`, branco `#FAFAFA`, cinza `#F4F4F4`/`#7A7A7A`, borda `#DBDBDA`; títulos em Pragmatica Extended (Adobe, paga) → aqui **Archivo**; cantos retos (`--r:2px`).
- Acento pedra/greige: `#B5AC9E` (escuro) / `#7A7166`–`#8C8478` (claro).
- **Escuro (padrão)**: fundo `#111111`, cartões `#1A1A1A`, cabeçalho `#212121`, barras `#E9E7E2`, linha `#B5AC9E`. **Claro**: fundo `#F4F4F4`, cartões brancos, barras `#212121`.
- **Largura expandida (`font-stretch:125%`) só em títulos**: `.brand-txt h1`, `.sh h2`, `.ovh .t`. **Botões de plataforma em largura normal** (`font-stretch:100%`, letter-spacing .08em) — pedido do Paulo em 20/11/2026 ("parece esticado"). Chips de período e rótulos dos big numbers também normais (expandidos cortavam "Ano até ontem").

## Fonte 1 · Meta Ads (PROVISÓRIA pela planilha)
- Conta **Dupllex** `1405527677145000` (BM Dupllex.imoveis `934781004433490`) ativa, mas **não liberada no conector oficial** (`is_ads_mcp_enabled:false`, "gradually being rolled out"; conferido em 17/11 e 20/11/2026). Não depende de permissão nem de reconectar.
- Decisão do Paulo em 20/11/2026: usar a planilha **até o MCP liberar**. `[BaseData] Dupllex - Meta` `1_eOdkIvt7JALyZeI5LBQ6HP9gqzQPKq8i1-WSQ-5Sg4`, aba **`Meta`** (gid 1978741298; ignorar `Meta-25` e `Página5`). Cabeçalho PT igual às BaseData do painel (Data … Formulario, Mensagem, Leads; A:Q), dados desde 06/2025.
- Leitura: achar a 1ª linha de 2026 pela coluna A (em 20/11: linha 2618; nunca colar a coluna inteira no contexto — usar a resposta salva em arquivo), ler `Meta!A<linha>:Q<última>`, pôr o cabeçalho na 1ª linha do JSON → `--meta`. `montar.compactar` faz o resto (só 2026).
- Regra: **Leads = Formulario + Mensagem** (regra do painel interno, não a da Meta). O `tx()` remove as trocas "WhatsApp → Site" da Meta. Rodapé diz que é provisória.
- Conferência (20/11/2026, até 19/11): 8.678 linhas, 26 campanhas, R$ 88.421,35, 2.814.192 impressões, 29.941 cliques no link, 914 leads (810 formulário, 104 WhatsApp). Mês a mês: jan 8.682,97 · fev 5.021,50 · mar 11.020,56 · abr 9.153,85 · mai 9.388,29 · jun 5.962,40 · jul 10.684,60 · ago 9.044,77 · set 8.545,09 · out 6.696,82 · nov (até 19) 4.220,50. WhatsApp quase zerado desde mai/26.
- **Quando liberar**: ler como a Montreal (`montar_montreal.ler_meta`, um mês por chamada, `level=ad`), passar o modelo em `dm`, voltar os textos da Meta (Site = lead − formulário) e trocar `FONTE_META`.

## Fonte 2 · Google Ads
- Conta **Dupllex** `1381273646`, `login_customer_id=4498709696` (MCC CREATIVEIMOB). Só `search_search`.
- Em 2026 só **uma Performance Max** `creativeimob_dupllex_conversao_google_pmax_jardins_no-brand` (19/08–10/09/2026): R$ 1.085,86, 78.159 impressões, 5.685 cliques, **0 conversões**. Parada desde 10/09.
- As 7 consultas de `tools/montar_gads.py`: `camp` tem 23 linhas (veio inline: gravar à mão); `ads`, `kw`, `conv_*` voltam vazias → gravar `[]`.
- Conversões da conta: ativas são WEBPAGE (`CI | Lead | Formulário | Comprador/Institucional/Proprietário venda`, `CI | Contato | WhatsApp`); as GA4 importadas estão ocultas.

## Fonte 3 · GA4
- Propriedade **dupllex.com.br** `529313528` (achada por `conversion_action.google_analytics_4_settings.property_id` no Google Ads; o conector não lista propriedades). Acesso liberado para paulo@creativeimob.com em 17/11/2026. Coleta desde **24/09/2026**.
- 5 consultas de `tools/ga4.py` salvas em `/tmp/dx/ga/dx_<q>.json` (cube, lp, ev, utm vão para arquivo). **`ct` diferente**: filtro `eventName EXACT generate_lead` + 9ª dimensão `customEvent:lead_method`; o script vira `generate_lead_whatsapp`/`_formulario`. O `ct` volta inline: dá para pedir só os dias novos e somar ao `dx_ct.json` anterior.
- **Contatos = generate_lead** (evento-chave, `lead_method` formulario/whatsapp). `contact_click` (cliques no WhatsApp) NÃO conta, para não duplicar.
- Conferência: até 19/11/2026, 4.963 sessões e 69 contatos. Meta chega com UTM (`meta / cpc`, campanha `…itaim-bibi_fernandes-51_site`). Em 19/11: 12 contatos, 9 de `/portfolio-atualizado` sem origem (provável teste; avisado ao Paulo).

## Como testar
- `node --check` no `<script>`; Playwright (bloquear `**/fonts.*/**`; `cimob-plat` = o/g/m/a; `shp-theme` dark/light) em 1360 e 400; `scrollWidth` = janela; `pageerror` vazio. Conferir com as fontes reais no navegador do app (Archivo muda larguras).

## Rotina e pendências
- **Ainda não está na tarefa diária** (`trig_018dybxSCkNo5bxAbZ7F7Exq`, 07:51): o prompt não pode ser lido daqui; o Paulo precisa colar o prompt atual para acrescentar o passo Dupllex (planilha Meta → Google 7 consultas → GA4 5 consultas → `montar_dupllex.py` → commit de `docs/dupllex/index.html` e `dados/dupllex_*.json`).
- Trocar a Meta pelo conector quando liberar; Google Ads sem gasto desde 10/09; confirmar os contatos de `/portfolio-atualizado`; validação do visual pelo Paulo.
- Só agregados; nunca dados pessoais de leads.
