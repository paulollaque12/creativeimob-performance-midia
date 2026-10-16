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
