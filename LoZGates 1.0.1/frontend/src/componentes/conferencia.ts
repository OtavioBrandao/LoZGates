/** Quanto tempo sem digitar antes de conferir a expressão no servidor. */
export const ESPERA_AO_DIGITAR = 300; // ms

export type ResultadoDaConferencia<T> = { texto: string; ok: true; valor: T } | { texto: string; ok: false; erro: unknown };

/**
 * Conferência "ao digitar": só pede ao servidor depois que o aluno para de
 * digitar por `espera` ms, e cada pedido novo cancela o anterior, tanto a
 * espera quanto a requisição que ainda estiver em andamento (AbortController).
 * Só a resposta do último pedido chega a `aoResultado`.
 */
export function criarConferencia<T>(
  conferir: (texto: string, sinal: AbortSignal) => Promise<T>,
  aoResultado: (resultado: ResultadoDaConferencia<T>) => void,
  espera = ESPERA_AO_DIGITAR,
) {
  let relogio: ReturnType<typeof setTimeout> | null = null;
  let emAndamento: AbortController | null = null;

  /** Cancela a espera e a requisição em andamento (campo vazio, tela fechada...). */
  const cancelar = () => {
    if (relogio !== null) clearTimeout(relogio);
    relogio = null;
    emAndamento?.abort();
    emAndamento = null;
  };

  const pedir = (texto: string) => {
    cancelar();
    relogio = setTimeout(() => {
      relogio = null;
      const controle = new AbortController();
      emAndamento = controle;
      const entregar = (resultado: ResultadoDaConferencia<T>) => {
        if (controle.signal.aborted) return; // um pedido mais novo já tomou o lugar deste
        emAndamento = null;
        aoResultado(resultado);
      };
      conferir(texto, controle.signal).then(
        (valor) => entregar({ texto, ok: true, valor }),
        (erro: unknown) => entregar({ texto, ok: false, erro }),
      );
    }, espera);
  };

  return { pedir, cancelar };
}
