"""
lozweb — camada de integração do LoZ Gates com o navegador.

Regra de ouro deste pacote: NENHUMA lógica do LoZ Gates mora aqui.
Toda a lógica (conversão, tabela verdade, equivalência, simplificação, circuitos
em pygame, banco de problemas, logs de uso, assistente de IA) continua nos
arquivos originais de BackEnd/ e FrontEnd/, que rodam SEM ALTERAÇÕES dentro do
Pyodide (CPython compilado para WebAssembly).

Este pacote só faz duas coisas:
  1. fornece ao código original aquilo que o desktop fornecia (Tkinter, rede,
     driver de vídeo do SDL) — ver plataforma.py, tkweb.py e rede.py;
  2. expõe funções simples para o React chamar — ver api.py.
"""
