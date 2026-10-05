import { useState, type KeyboardEvent } from 'react';
import { api, ErroDaApi, mensagemDe } from '../api/cliente';
import { Botao } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { registrar } from '../telemetria/registro';

/**
 * Tela "Equivalência Lógica" (EquivalenceScreen + EquivalenceController).
 * A comparação é só por tabela-verdade (D3d).
 */
export function Equivalencia() {
  const app = useAplicacao();
  const janelas = useJanelas();
  // on_back() limpa os campos e o resultado; aqui isso vem de graça porque o estado é desta tela
  const [expressao1, setExpressao1] = useState('');
  const [expressao2, setExpressao2] = useState('');
  const [resultado, setResultado] = useState<boolean | null>(null);
  const [comparando, setComparando] = useState(false);

  const comparar = async () => {
    const e1 = expressao1.trim().toUpperCase();
    const e2 = expressao2.trim().toUpperCase();
    if (!e1 || !e2) {
      janelas.popupErro('As expressões não podem estar vazias.');
      return;
    }
    setComparando(true);
    try {
      const { equivalentes } = await api.equivalencia(e1, e2);
      registrar('log_equivalence_check_with_expressions', e1, e2, equivalentes);
      setResultado(equivalentes);
    } catch (erro) {
      // Expressão inválida (ValueError no desktop) só gera o aviso; outros erros também vão para o registro
      if (!(erro instanceof ErroDaApi && erro.tipo === 'expressao_invalida')) {
        registrar('log_error', 'equivalence_check_error', mensagemDe(erro), 'comparar_function');
        janelas.popupErro(`Erro ao comparar expressões: ${mensagemDe(erro)}`);
      } else {
        janelas.popupErro(mensagemDe(erro));
      }
    } finally {
      setComparando(false);
    }
  };

  const aoTeclar = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') void comparar();
  };

  return (
    <main className="tela tela--estreita">
      <section className="formulario-central cartao-formulario" aria-labelledby="titulo-equivalencia">
        <h1 id="titulo-equivalencia" className="titulo-formulario">
          ⟺&nbsp;&nbsp;Equivalência Lógica
        </h1>
        <p className="texto-secundario">Digite as duas expressões e verifique se são logicamente equivalentes.</p>

        <label className="rotulo-campo" htmlFor="expressao-a">
          Expressão A:
        </label>
        <input
          id="expressao-a"
          className="campo campo--expressao"
          placeholder="Ex.: P > Q"
          value={expressao1}
          spellCheck={false}
          autoComplete="off"
          autoFocus
          onChange={(e) => setExpressao1(e.target.value)}
          onKeyDown={aoTeclar}
        />
        <p className="separador-comparar" aria-hidden="true">
          <span>⟺&nbsp;&nbsp;comparar</span>
        </p>
        <label className="rotulo-campo" htmlFor="expressao-b">
          Expressão B:
        </label>
        <input
          id="expressao-b"
          className="campo campo--expressao"
          placeholder="Ex.: !P | Q"
          value={expressao2}
          spellCheck={false}
          autoComplete="off"
          onChange={(e) => setExpressao2(e.target.value)}
          onKeyDown={aoTeclar}
        />

        <div className="pilha-botoes">
          <Botao estilo="sucesso" onClick={() => void comparar()} disabled={comparando}>
            ⟺&nbsp;&nbsp;Comparar Expressões
          </Botao>
        </div>

        <div role="status" aria-live="polite">
          {resultado !== null && (
            <p className={`resultado-equivalencia ${resultado ? 'resultado-equivalencia--sim' : 'resultado-equivalencia--nao'}`}>
              {resultado ? '✓  São equivalentes!' : '✕  Não são equivalentes'}
            </p>
          )}
        </div>

        <div className="pilha-botoes">
          <Botao estilo="voltar" onClick={() => app.mostrarTela('inicio')}>
            Voltar
          </Botao>
        </div>
      </section>
    </main>
  );
}
