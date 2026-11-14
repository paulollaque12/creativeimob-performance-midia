---
name: montreal-dashboard-performance
description: Página de performance da Montreal Business (performance.creativeimob.app/montreal/): Overview, Google Ads e Meta Ads num link só (GA4 pendente de acesso). Use para qualquer ajuste, dado, validação, publicação ou caso pontual da Montreal.
---

# Montreal Business · Dashboard de performance

Skill específica da Montreal. O que é comum a todos os clientes (painel interno, Cérebro, métricas, motor de gráficos, template único, rotina geral) está na skill mãe `creativeimob-dashboard-performance`; a Taylor tem a sua (`taylor-dashboard-performance`), e a página da Montreal reaproveita a estrutura dela. Leia a mãe quando mexer no template.

## O cliente
- **Montreal Business Imobiliária** (montrealbusiness.com.br, CRECI PJ 30023J): imobiliária da Zona Leste de SP, escritório na R. Airi, 227, Tatuapé. Venda de apartamentos, coberturas, studios, lançamentos; campanhas de Tatuapé e Anália Franco; recruta corretores ("Seja um corretor").
- Cliente da CreativeImob. Quem pede: **Paulo** (Data & BI, paulo@creativeimob.com). Português do Brasil (às vezes espanhol: responder no idioma da mensagem); padrão "extremamente elegante", "muito sênior".
- Página **entregue ao cliente**: só dados da Montreal no código, identidade da Montreal, sem Cérebro, sem nada da Taylor (nem nomes, IDs, comentários). Site público, sem senha.

## Onde está
- **Link**: https://performance.creativeimob.app/montreal/ (`docs/montreal/index.html`). Repositório `paulollaque12/creativeimob-performance-midia`, branch `main`, GitHub Pages em `/docs`.
- Gerador: `tools/montar_montreal.py`. Uso: `python3 tools/montar_montreal.py --gads /tmp/mt/gads --ate ONTEM /tmp/mt/meta/*.json` → `docs/montreal/index.html` + `dados/montreal_gads.json` (sem `--gads` reaproveita a cópia). GA4 entra sozinho quando existir `dados/montreal_ga4.json`.
- Outros arquivos: `fonte/montreal_logo.json` (máscaras PNG base64 do ícone e do nome, tiradas do logo enviado pelo Paulo em 14/11/2026), `ATUALIZAR.md` seção "Montreal Business".
- Acesso ao repo no sandbox: `add_repo` (owner `paulollaque12`, repo `creativeimob-performance-midia`, access `push`) + `git clone --depth 1` + `register_repo_root`. Antes do push: `git pull --rebase`. Deploy: `gh api repos/paulollaque12/creativeimob-performance-midia/actions/runs?per_page=1` ("pages build and deployment" `success` com o sha). Não commitar `tools/__pycache__`.

## Como a página é feita (importante)
- **Reaproveita a chave `ty` do template** (`montar.solo(..., "ty", "montreal", ...)`): Overview, Meta, Google, abas, Insights e acabamento são os mesmos da Taylor. Depois o script troca a identidade **só no arquivo gerado** (`identidade()`):
  - substitui os três blocos de tokens `:root[data-client="ty"]` (claro, escuro do sistema, escuro forçado) por `TOK_CLARO`/`TOK_ESCURO`;
  - troca as cores fixas do acabamento da Taylor (lista `CORES`: ouro/latão/marfim/verde → turquesa/grafite);
  - cantos: `border-radius` 3px→8px e 2px→6px nas regras `ty`; topo 18px (14px no celular) + `CSS_EXTRA`;
  - fonte: Josefin Sans + Inter → **Plus Jakarta Sans** no `<link>` e nos tokens;
  - marca: `MARCA_TY` → `<div class="mk-mt"><i class="mtc"></i><i class="mtw"></i></div>` (ícone turquesa + nome claro);
  - textos via `trocas` (nome do cliente, "site" quando não há GA4) e limpeza de restos do painel interno (opções do filtro de imobiliárias, rodapé do Cérebro, comentários com "Taylor").
- O script avisa se sobrar "Taylor" fora do `<style>`. Conferir sempre: `grep -c Taylor docs/montreal/index.html` = 0.
- Consequência: **mudanças no template para a Taylor também chegam à Montreal** (bom para correções; cuidado com textos específicos da Taylor: se aparecerem, acrescentar em `trocas`). Ao mexer no template, regerar as duas páginas.

## Identidade visual (do site; não reverter sem pedido)
- Site montrealbusiness.com.br (variáveis CSS lidas no navegador do app): primária **turquesa `#13D1D1`**, secundária `#E0F2F7`, texto `#374151` / `#6B7280`, escuros `#1F2937` / `#111827`, fundo `#F9F9F9`, bordas `#E5E7EB`; fonte **Plus Jakarta Sans** (Roboto de reserva); cantos arredondados (6–16px). O logo do site é PNG dentro de SVG (não há vetor).
- **Escuro (padrão da página, como a Taylor)**: fundo `#0B0F14`, cartões `#121821`, cabeçalho `#18212D`, barras turquesa `#13D1D1`, linha `#E5E7EB`, funil turquesa → `#0F3436` → `#0E8F8F`, Google nas barras da Overview `#8B95A3`.
- **Claro**: fundo `#F4F6F8`, cartões brancos, cabeçalho grafite `#1F2937`, barras `#13C4C4`, linha grafite `#374151`, números de seção `#0B9A9A`.
- Cabeçalho com brilho turquesa discreto no canto (radial), moldura fina turquesa, períodos como abas com traço turquesa (letter-spacing .12em, gap 24px para "Ano até ontem" caber em 1360px).

## Fonte 1 · Meta Ads
- Conta **C.A. Montreal Business Imob** `1210410723539965` (BM Montreal Business `796118392106309`).
- Mesma receita da Taylor: `mcp__Meta_Ads__ads_get_ad_entities`, **um mês por chamada**, `level=ad`, `time_increment="1"`, `fields=[id,name,campaign_name,adset_name,amount_spent,impressions,clicks,link_click,lead,onsite_conversion_lead_grouped]`, `filtering=[impressions GREATER_THAN 0]`, `limit=1000`, `reporting_purpose=["metric_lookup"]`, `include_additional_context=false`. Meses de 2–3 mil linhas vieram inteiros, sem cursor. Respostas vão para arquivo → copiar para `/tmp/mt/meta/AAAA-MM.json`.
- **Set/26 sem veiculação** (não chamar ou aceitar vazio). Gasto caiu de R$ 4–6,7 mil/mês (jan–ago) para ~R$ 1,1 mil/mês (out–nov).
- Todos os leads são de **formulário** (lead = onsite_conversion_lead_grouped; "Site" = 0). Leads = `lead`; cliques = `link_click`.
- 24 campanhas em 2026. Nomes no padrão `lead_eleya_tatuape_formulario`, `video_apto-eleya_marcos_v2`, `video_open-mind_chacara-sto-antonio_…`.

## Fonte 2 · Google Ads
- Conta **Montreal Business Imóveis** `6154519094`, `login_customer_id=4498709696` (MCC CREATIVEIMOB). Só `mcp__Google_Ads__search_search` (nunca as ferramentas de escrita sem pedido).
- As 7 consultas de `tools/montar_gads.py` (2026-01-01 até ONTEM) em `/tmp/mt/gads/`. **Armadilha**: respostas pequenas vêm inline e não ficam em disco; para `ads` e `camp`, acrescentar campos extras (`customer.descriptive_name`, `campaign.id`, `segments.day_of_week`, `metrics.all_conversions`, `metrics.interactions`, `metrics.average_cpc`…) para a resposta passar do limite e ir para arquivo; `adinfo` e `conv_*` são pequenos: gravar o JSON à mão. `campaign.start_date` não existe na API.
- Uma campanha só: `creativeimob_montreal-business_search_no-brand_tatuapé_apartamentos-v2` (desde 26/05/2026; grupos `apartamentos_venda_tatuape`, `generico_tatuape`, `familia_3_4_dorm`, `analia_franco`). **Sem gasto desde 09/11/2026.**
- Conversões (Leads = todas as conversões, regra do Paulo): `[Site] Whatsapp Flutuante (11) 93299-6481` → WhatsApp; `[Site] [/imoveis] [Formulário] Enviar Mensagem` → Formulário; **`[Site] [/imoveis] view_item` está como conversão principal** e entra como lead (classe "R": só no total, não em formulário/WhatsApp). Em out/26 foram 10 das 16 conversões. Ponto levado ao Paulo: tirar `view_item` de conversão principal na conta, ou excluí-la dos leads na página (uma linha).
- Ações vinculadas a GA4 na conta (todas ocultas): propriedades `290629683` "Montreal Business – GA4", `258046319` "Montreal Business", `508560208` "montreal business".

## Fonte 3 · GA4 (pendente)
- **Sem acesso**: as três propriedades acima respondem "User does not have sufficient permissions" para paulo@creativeimob.com. O conector GA4 não lista propriedades (ver doc do projeto `claude/mcp_ga4.md`).
- Sem `dados/montreal_ga4.json` a página sai **sem o botão GA4** e a Overview troca os big numbers de site (Sessões, Contatos) por **Impressões e CTR** e a faixa "Impressões" por "Clique → lead" (código guardado por `O.s` no template). Textos "e site" são removidos via `trocas` (`sem_site`).
- Quando vier o acesso: descobrir qual propriedade coleta (testar as três), rodar as 5 consultas de `tools/ga4.py` para ela, gerar o arquivo no formato de `dados/ga4.json` (chave `ty`) como `dados/montreal_ga4.json`, rever a regex de contatos (eventos da Montreal) e regerar. Os botões e a aba GA4 da Taylor passam a valer aqui.

## Números de conferência (14/11/2026, dados até 13/11)
- Meta 2026: R$ 44.265,59 · 666.729 impressões · 9.857 cliques no link · 606 leads (jan 65, fev 58, mar 84, abr 100, mai 82, jun 68, jul 64, ago 47, set 0, out 12, nov 26). 4.479 linhas.
- Google 2026: R$ 5.617,73 (conector por mês R$ 5.617,69: diferença de arredondamento) · 47.259 impressões · 4.248 cliques · 33 conversões (20 WhatsApp, 3 formulário, 10 view_item); mai R$ 350 · jun 1.520 · jul 1.520 · ago 653 · set 420 · out 912 · nov 243.
- Overview 01–13/11: R$ 1.431,56 (83% Meta), 26 leads, CPL R$ 55,06; Google 0 conversões em novembro.

## Rotina
- **Ainda não está na tarefa diária** "Atualizar painel de mídia CreativeImob" (`trig_018dybxSCkNo5bxAbZ7F7Exq`, 07:51): o prompt não pode ser lido daqui e `update_trigger` substitui o prompt inteiro. Para incluir: o Paulo cola o prompt atual (ou o painel da tarefa) e acrescenta-se o passo "3c Montreal": Meta (um mês por chamada, só o mês corrente e o anterior se quiser poupar chamadas, mas o gerador precisa do ano inteiro em `/tmp/mt/meta/`) → Google (7 consultas) → `montar_montreal.py --gads /tmp/mt/gads --ate ONTEM` → commit de `docs/montreal/index.html` e `dados/montreal_gads.json`.
- Atualização manual: refazer as consultas do ano inteiro até ONTEM e rodar o gerador; conferir os totais acima mês a mês com `level=account`/`segments.month`.

## Como testar
- `node --check` no `<script>` extraído; Playwright (bloquear `**/fonts.*/**`; `localStorage` `cimob-plat` = o/g/m e `shp-theme` = dark/light) em 1360 escuro e claro, 1100, 820 e 400; `scrollWidth` = janela; `pageerror` vazio; clicar Overview/Google/Meta e conferir o `main` visível; "Ano até ontem" com os totais de conferência.
- Conferir com as fontes reais no navegador do app (site montrealbusiness.com.br e performance.creativeimob.app já liberados).

## Decisões e pendências
- Tema padrão escuro (igual à Taylor); identidade turquesa + grafite. Ainda não validado pelo Paulo em tela.
- Pendente: acesso GA4; decisão sobre `view_item` nos leads; passo na tarefa diária; Google sem gasto desde 09/11.
- Só agregados; nunca dados pessoais de leads.
