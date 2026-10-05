import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { criarConferencia, ESPERA_AO_DIGITAR, type ResultadoDaConferencia } from './conferencia';

/** Requisição falsa: guarda o texto e o sinal de cada pedido e deixa o teste decidir quando responder. */
function servidorFalso() {
  const pedidos: { texto: string; sinal: AbortSignal; responder: (valor: string) => void }[] = [];
  const conferir = vi.fn(
    (texto: string, sinal: AbortSignal) =>
      new Promise<string>((responder) => {
        pedidos.push({ texto, sinal, responder });
      }),
  );
  return { pedidos, conferir };
}

describe('conferência ao digitar', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('espera ~300 ms sem digitação antes de chamar o servidor, e só com o último texto', () => {
    const { conferir } = servidorFalso();
    const { pedir } = criarConferencia(conferir, () => {});
    expect(ESPERA_AO_DIGITAR).toBe(300);

    pedir('A');
    vi.advanceTimersByTime(120);
    pedir('A &');
    vi.advanceTimersByTime(120);
    pedir('A & B');
    vi.advanceTimersByTime(ESPERA_AO_DIGITAR - 1);
    expect(conferir).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);
    expect(conferir).toHaveBeenCalledTimes(1);
    expect(conferir.mock.calls[0][0]).toBe('A & B');
  });

  it('um pedido novo cancela a requisição que ainda está em andamento', async () => {
    const { pedidos, conferir } = servidorFalso();
    const resultados: ResultadoDaConferencia<string>[] = [];
    const { pedir } = criarConferencia(conferir, (r) => resultados.push(r));

    pedir('A &');
    vi.advanceTimersByTime(ESPERA_AO_DIGITAR);
    expect(pedidos).toHaveLength(1);

    pedir('A & B');
    expect(pedidos[0].sinal.aborted).toBe(true); // a requisição antiga foi abortada
    vi.advanceTimersByTime(ESPERA_AO_DIGITAR);
    expect(pedidos).toHaveLength(2);
    expect(pedidos[1].sinal.aborted).toBe(false);

    // mesmo que a resposta antiga chegue depois, ela não aparece
    pedidos[1].responder('válida');
    pedidos[0].responder('inválida');
    await vi.runAllTimersAsync();
    expect(resultados).toEqual([{ texto: 'A & B', ok: true, valor: 'válida' }]);
  });

  it('cancelar (campo vazio ou tela fechada) aborta a espera e a requisição', async () => {
    const { pedidos, conferir } = servidorFalso();
    const aoResultado = vi.fn();
    const conferencia = criarConferencia(conferir, aoResultado);

    conferencia.pedir('A');
    vi.advanceTimersByTime(ESPERA_AO_DIGITAR);
    conferencia.pedir('A |');
    conferencia.cancelar();
    vi.advanceTimersByTime(ESPERA_AO_DIGITAR * 3);

    expect(pedidos).toHaveLength(1);
    expect(pedidos[0].sinal.aborted).toBe(true);
    pedidos[0].responder('tarde demais');
    await vi.runAllTimersAsync();
    expect(aoResultado).not.toHaveBeenCalled();
  });

  it('erros do servidor chegam como resultado, com o texto conferido', async () => {
    const erro = new Error('fora do ar');
    const resultados: ResultadoDaConferencia<string>[] = [];
    const { pedir } = criarConferencia(() => Promise.reject(erro), (r) => resultados.push(r));
    pedir('A');
    await vi.advanceTimersByTimeAsync(ESPERA_AO_DIGITAR);
    expect(resultados).toEqual([{ texto: 'A', ok: false, erro }]);
  });
});
