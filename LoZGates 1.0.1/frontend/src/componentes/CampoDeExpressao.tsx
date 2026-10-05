import { useEffect, useImperativeHandle, useLayoutEffect, useRef, useState, type Ref } from 'react';
import { api, ErroDaApi, mensagemDe } from '../api/cliente';

export interface ControleDoCampo {
  focar: () => void;
  /** Insere o texto no lugar do cursor (ou da seleção) e devolve o foco ao campo. */
  inserir: (texto: string) => void;
}

type Analise =
  | { estado: 'vazio' }
  | { estado: 'conferindo' }
  | { estado: 'valida'; booleana: string; variaveis: string[] }
  | { estado: 'invalida'; mensagem: string; posicao: number | null; texto: string }
  | { estado: 'sem-servidor'; mensagem: string };

interface Props {
  id: string;
  rotulo: string;
  valor: string;
  aoMudar: (valor: string) => void;
  /** Enter no campo */
  aoConfirmar?: () => void;
  aoFocar?: () => void;
  placeholder?: string;
  ref?: Ref<ControleDoCampo>;
}

/** Espera o aluno parar de digitar antes de conferir a expressão no servidor. */
const ESPERA = 350;

/**
 * Campo de uma expressão lógica. Enquanto o aluno digita, o parser canônico
 * (pelo /api/expressao/analisar) diz se a expressão é válida, quais são as
 * variáveis e como ela fica em álgebra booleana, ou aponta onde está o erro.
 * É só um aviso: os botões de cada tela continuam fazendo o que faziam.
 */
export function CampoDeExpressao({ id, rotulo, valor, aoMudar, aoConfirmar, aoFocar, placeholder, ref }: Props) {
  const campo = useRef<HTMLInputElement>(null);
  const cursorDepoisDeInserir = useRef<number | null>(null);
  const pedido = useRef(0);
  const [analise, setAnalise] = useState<Analise>({ estado: 'vazio' });

  useImperativeHandle(
    ref,
    () => ({
      focar: () => campo.current?.focus(),
      inserir: (texto: string) => {
        const elemento = campo.current;
        const inicio = elemento?.selectionStart ?? valor.length;
        const fim = elemento?.selectionEnd ?? inicio;
        cursorDepoisDeInserir.current = inicio + texto.length;
        aoMudar(valor.slice(0, inicio) + texto + valor.slice(fim));
      },
    }),
    [valor, aoMudar],
  );

  // Depois de uma inserção pelo teclado de operadores, o cursor fica logo depois do símbolo
  useLayoutEffect(() => {
    const posicao = cursorDepoisDeInserir.current;
    if (posicao === null) return;
    cursorDepoisDeInserir.current = null;
    campo.current?.focus();
    campo.current?.setSelectionRange(posicao, posicao);
  }, [valor]);

  useEffect(() => {
    const texto = valor.trim();
    const atual = ++pedido.current;
    if (!texto) {
      setAnalise({ estado: 'vazio' });
      return;
    }
    setAnalise((anterior) => (anterior.estado === 'vazio' ? { estado: 'conferindo' } : anterior));
    const relogio = window.setTimeout(() => {
      api
        .analisarExpressao(texto)
        .then((resposta) => {
          if (atual !== pedido.current) return;
          setAnalise(
            resposta.valida
              ? { estado: 'valida', booleana: resposta.expressao_booleana, variaveis: resposta.variaveis }
              : { estado: 'invalida', mensagem: resposta.mensagem, posicao: resposta.posicao, texto },
          );
        })
        .catch((erro: unknown) => {
          if (atual !== pedido.current) return;
          // Texto que nem chega a ser analisado (longo demais, por exemplo) também é inválido
          if (erro instanceof ErroDaApi && erro.status === 422) {
            setAnalise({ estado: 'invalida', mensagem: erro.message, posicao: erro.posicao, texto });
          } else {
            setAnalise({ estado: 'sem-servidor', mensagem: mensagemDe(erro) });
          }
        });
    }, ESPERA);
    return () => window.clearTimeout(relogio);
  }, [valor]);

  const idAnalise = `${id}-analise`;
  return (
    <div className="campo-expressao">
      <label className="rotulo-campo" htmlFor={id}>
        {rotulo}
      </label>
      <input
        ref={campo}
        id={id}
        className={`campo campo--expressao ${analise.estado === 'invalida' ? 'campo--invalido' : ''}`}
        placeholder={placeholder}
        value={valor}
        spellCheck={false}
        autoCapitalize="characters"
        autoComplete="off"
        aria-describedby={idAnalise}
        aria-invalid={analise.estado === 'invalida'}
        onChange={(e) => aoMudar(e.target.value)}
        onFocus={aoFocar}
        onKeyDown={(e) => {
          if (e.key === 'Enter') aoConfirmar?.();
        }}
      />
      <p id={idAnalise} className={`campo-expressao__analise campo-expressao__analise--${analise.estado}`} aria-live="polite">
        {analise.estado === 'vazio' && 'Use letras de A a Z, as constantes 0 e 1 e os operadores abaixo.'}
        {analise.estado === 'conferindo' && 'Conferindo…'}
        {analise.estado === 'valida' && (
          <>
            <span className="campo-expressao__marca">✓ Válida</span>
            <span>{analise.variaveis.length ? `variáveis ${analise.variaveis.join(', ')}` : 'sem variáveis'}</span>
            <span>
              álgebra booleana <span className="mono">{analise.booleana}</span>
            </span>
          </>
        )}
        {analise.estado === 'invalida' && (
          <>
            <span className="campo-expressao__marca">✕ {analise.mensagem}</span>
            {analise.posicao !== null && analise.posicao >= 0 && (
              <span className="mono campo-expressao__trecho" aria-label={`Erro na posição ${analise.posicao + 1}`}>
                {analise.texto.slice(0, analise.posicao)}
                <mark>{analise.texto[analise.posicao] ?? '␣'}</mark>
                {analise.texto.slice(analise.posicao + 1)}
              </span>
            )}
          </>
        )}
        {analise.estado === 'sem-servidor' && analise.mensagem}
      </p>
    </div>
  );
}
