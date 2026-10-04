/**
 * Executa com fetch() as requisições que o código Python original tentou fazer com
 * `requests.post(...)` (ver python/lozweb/rede.py para o fluxo em duas fases).
 */

export interface PedidoHttp {
  metodo: string;
  url: string;
  params?: Record<string, string> | null;
  cabecalhos: Record<string, string>;
  json?: unknown;
  form?: Record<string, string> | null;
  corpo?: string | null;
  timeout?: number | null;
}

export interface RespostaRede {
  status?: number;
  texto?: string;
  erro?: string;
  timeout?: boolean;
}

export async function executarPedido(pedido: PedidoHttp, { semCors = false } = {}): Promise<RespostaRede> {
  const controle = new AbortController();
  const segundos = pedido.timeout ?? 30;
  const relogio = setTimeout(() => controle.abort(), segundos * 1000);
  try {
    const cabecalhos: Record<string, string> = { ...pedido.cabecalhos };
    let corpo: BodyInit | undefined;
    if (pedido.json !== undefined && pedido.json !== null) {
      corpo = JSON.stringify(pedido.json);
      if (!Object.keys(cabecalhos).some((c) => c.toLowerCase() === 'content-type')) {
        cabecalhos['Content-Type'] = 'application/json';
      }
    } else if (pedido.form) {
      corpo = new URLSearchParams(pedido.form);
    } else if (pedido.corpo) {
      corpo = pedido.corpo;
    }
    let url = pedido.url;
    if (pedido.params) url += (url.includes('?') ? '&' : '?') + new URLSearchParams(pedido.params);

    const resposta = await fetch(url, {
      method: pedido.metodo,
      headers: semCors ? undefined : cabecalhos,
      body: corpo,
      signal: controle.signal,
      mode: semCors ? 'no-cors' : 'cors',
    });
    // Envio "no-cors" (Google Forms): o navegador não deixa ler a resposta.
    // Se chegou até aqui, o formulário recebeu os dados — equivale ao 200 do desktop.
    if (resposta.type === 'opaque') return { status: 200, texto: '' };
    return { status: resposta.status, texto: await resposta.text() };
  } catch (erro) {
    if (controle.signal.aborted) {
      return { erro: `Tempo de resposta esgotado (${segundos}s)`, timeout: true };
    }
    return { erro: erro instanceof Error ? erro.message : String(erro) };
  } finally {
    clearTimeout(relogio);
  }
}
