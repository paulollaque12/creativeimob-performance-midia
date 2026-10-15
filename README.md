# CreativeImob · Performance de mídia

Painel de mídia paga (Meta Ads) dos clientes da CreativeImob, feito pela equipe de Data & BI.
Publicado sem senha no GitHub Pages a partir da pasta `docs/`.

- **Cérebro**: compilado das imobiliárias (custos, formatos, públicos, bairros, faixas de valor e criativos).
- **SH Prime**, **Nova SP** e **Lopes Prime**: painel de cada cliente, com as cores da marca.

## Estrutura
| Caminho | O que é |
|---|---|
| `fonte/template.html` | Código do painel (HTML, CSS e JS num arquivo só), com os marcadores `/*__DATA_SH__*/null`, `/*__DATA_NSP__*/null`, `/*__DATA_LP__*/null` e `/*__AT__*/`. É a mesma fonte do artefato do Claude. |
| `tools/montar.py` | Lê as respostas do conector Google Sheets, aplica as regras (só 2026, números pt-BR) e gera `docs/index.html`. |
| `docs/` | Site publicado (`index.html`, `robots.txt`, `.nojekyll`). |
| `ATUALIZAR.md` | Rotina de atualização passo a passo. |
| `CONTEXTO.md` | Fontes, métricas, regras de negócio e decisões de design. |

## Fontes
| Cliente | Planilha | Aba |
|---|---|---|
| SH Prime | `[BaseData] SH Prime - Meta` (`1tSgEdMFQKXgaRf-LxNuDTUfHIM3pTlhiJ-NF15bBSps`) | Meta |
| Nova SP | `[BaseData] Nova São Paulo - Meta` (`1cbrG6udFXUzYvpxEVb6m0ru8A0oD_DUgeEMn5ZsRpUo`) | Meta |
| Lopes Prime | `[BaseData] Lopes Prime - Meta` (`16eTUPB8t0bBBroTn3kQyVqq6SrRsajPMK0DMwkILG6Y`) | Meta |
