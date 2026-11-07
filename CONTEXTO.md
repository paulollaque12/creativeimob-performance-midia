# Contexto do projeto

## Origem
Pedido de Paulo (Data & BI, CreativeImob) em 10/10/2026: replicar o dashboard de performance do Looker Studio da SH Prime em HTML, "mais bonito, elegante, sofisticado, respeitando as cores do cliente, de um jeito sênior, com descrições antes dos blocos", no mesmo padrão do painel da Gralha. Depois vieram a Nova São Paulo (14/10), a aba Cérebro (14/10) a Lopes Prime (15/10) e a Taylor (15/10), que compila as imobiliárias.

## Dados (aba Meta das planilhas [BaseData]; na Taylor, aba [BASE] meta da planilha [TAYLOR] report semanal)
- As colunas são localizadas pelo nome do cabeçalho, em português ou em inglês (a Taylor usa Date, Campaign Name, Adset Name, Spend..., Action Link Clicks).
- Colunas A..Q: Data, ID Campaign, Campaign, ID Ad Group, Ad Group, ID Ad, Ad Name, Investimento, Impressões, Cliques, Link Cliques, Leads Meta, Leads Site, Mensagens, Formulario, Mensagem, Leads.
- Uma linha por dia por anúncio. Números em texto pt-BR. **Só 2026.**
- Leads = Formulario + Mensagem (WhatsApp = coluna P "Mensagem", não a N "Mensagens").

## Métricas
- Cliques = Link Cliques. CTR = cliques ÷ impressões. CPM = invest ÷ impressões × 1000. CPC = invest ÷ cliques. CPL (custo por conversão) = invest ÷ leads. Tx. conv. = leads ÷ impressões.
- Comparação: mesmos dias do mês anterior quando o período está dentro de um mês; senão, período anterior de mesmo tamanho. Validado com o PDF do Looker da SH Prime (01–09/10/2026: R$ 1.724,90, 60.966 impressões, 3.271 cliques, 70 leads, CPL R$ 24,64).

## Design
- Coluna central de 1080 px (igual à Gralha), cabeçalho escuro arredondado, frase cinza antes de cada bloco, modo claro/escuro.
- Abas: Cérebro (grafite + vermelho CreativeImob), SH Prime (ouro + grafite), Nova SP (azul-marinho + azul-céu do logo), Lopes Prime (preto e branco; logo extraído da imagem enviada e usado como máscara CSS), Taylor (verde-inglês do logo + latão; brasão e "TAYLOR IMÓVEIS" extraídos da imagem enviada).
- Gráficos combinados com eixo Y1 (barras) e Y2 (linhas), valores das linhas sempre visíveis.

## Cérebro: taxonomia lida dos nomes
Formato (vídeo animado, vídeo, carrossel, imagem estática, catálogo, post), apresentação do vídeo (com apresentador ou só o imóvel), tipo de campanha, público (Advantage+, aberto, interesses, remarketing, raio geográfico...), bairro (lista normalizada), faixa de valor (lida de "1.5mi", "750mil") tipo de imóvel e venda ou locação. As regras estão em `fonte/template.html`, seção "CÉREBRO".

## Publicação
- Site sem senha (decisão do usuário em 14/10/2026), com `noindex` e `robots.txt` para não aparecer em buscadores. Qualquer pessoa com o link vê os números.
- No site não há leitura ao vivo: ele mostra a cópia gerada na última atualização. O artefato do Claude lê as planilhas ao vivo pelo conector.

## Página da Taylor direto da Meta (06/11/2026)
- Pedido do usuário: "um link só com os dados de meta da Taylor no mesmo domínio", "tem que vir diretamente do MCP de Meta".
- Endereço: https://performance.creativeimob.app/taylor/ · gerada por `tools/montar_meta.py` (usa `montar.solo`): sem abas, sem Cérebro, só os dados da Taylor no código, IDs das planilhas removidos.
- Fonte: conector oficial Meta Ads, conta 3063928683998040, nível anúncio, por dia. A Meta tem gasto desde 11/04/2026 (a planilha só desde 27/04).
- Leads = `lead` (formulário + site). Formulário = `onsite_conversion_lead_grouped`. Site = diferença. Sem WhatsApp (o conector não expõe conversas).
- Conferência na criação (até 05/11/2026): 2.387 linhas, 13 campanhas, R$ 42.160,87, 923 leads (698 formulário, 225 site). Investimento e cliques por mês iguais à planilha de maio a novembro.
