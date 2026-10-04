# Oráculo congelado do `interface_update`

Cópia **somente leitura** da lógica do LoZ Gates como ela estava em
`origin/interface_update` (commit registrado em `MANIFESTO.json`), antes da
migração para o parser canônico. Ela serve de referência para os testes de
paridade (`tests/paridade/`): o resultado da versão nova tem que ser idêntico
ao desta cópia, exceto nas diferenças aprovadas listadas em
`tests/paridade/diferencas_aprovadas.py`.

- **Nada aqui é importado pelo aplicativo.** Só os testes usam.
- **Não edite estes arquivos.** A única alteração em relação ao original é
  mecânica: os imports absolutos `BackEnd...`, `FrontEnd...` e `config` foram
  prefixados com `tests.paridade.oraculo_interface_update.` para que a cópia
  não carregue os módulos novos. `test_integridade_oraculo.py` desfaz essa troca e confere o
  SHA-256 de cada arquivo contra o manifesto.
- Alguns módulos dependem de `pygame`, `tkinter` ou `customtkinter` (como no
  original). Os testes que precisam deles são pulados se o pacote não estiver
  instalado.
