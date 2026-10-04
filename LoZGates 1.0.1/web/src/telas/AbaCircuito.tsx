import { useEffect, useRef, useState } from 'react';
import { dadosFixos, mensagemDe } from '../api/cliente';
import { Botao } from '../componentes/Botao';
import { CircuitoEstatico } from '../circuito/CircuitoEstatico';
import { exportarPng } from '../circuito/exportarPng';
import { PREFIXO_LABEL_CIRCUITO, useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';

/** Aba "Circuito": o circuito da expressão, calculado no servidor (layout em JSON) e desenhado em SVG. */
export function AbaCircuito() {
  const app = useAplicacao();
  const janelas = useJanelas();
  const svg = useRef<SVGSVGElement>(null);
  const [duvida, setDuvida] = useState<string | null>(null);

  useEffect(() => {
    dadosFixos
      .conteudo()
      .then((c) => setDuvida(c.duvida_circuitos))
      .catch(() => setDuvida(null));
  }, []);

  // salvar_imagem()
  const salvarImagem = async () => {
    if (!app.layout || !svg.current) {
      janelas.popupErro('Imagem não encontrada.');
      return;
    }
    try {
      await exportarPng(svg.current, app.layout, 'circuito.png');
      janelas.popupErro('Imagem salva com sucesso!', 'LoZ Gates');
    } catch (erro) {
      janelas.popupErro(`Erro ao salvar imagem: ${mensagemDe(erro)}`);
    }
  };

  const expressao = app.labelCircuito.startsWith(PREFIXO_LABEL_CIRCUITO)
    ? app.labelCircuito.slice(PREFIXO_LABEL_CIRCUITO.length)
    : app.labelCircuito;

  return (
    <div className="aba-circuito">
      <div className="aba-circuito__barra">
        <p className="aba-circuito__rotulo">
          <span className="texto-secundario">Expressão Lógica Proposicional:</span> <span className="mono destaque">{expressao}</span>
        </p>
        <button
          type="button"
          className="botao-duvida"
          aria-label="Ajuda rápida sobre circuitos"
          disabled={duvida === null}
          onClick={() => duvida !== null && janelas.popupDuvida(duvida)}
        >
          ?
        </button>
      </div>

      <figure className="aba-circuito__figura">
        {app.layout ? (
          <CircuitoEstatico ref={svg} layout={app.layout} rotulo={`Circuito lógico de ${expressao}`} />
        ) : (
          <figcaption className="texto-secundario">{app.gerandoCircuito ? 'Gerando circuito…' : app.textoCircuito}</figcaption>
        )}
      </figure>

      <div className="linha-botoes">
        <Botao onClick={() => void salvarImagem()}>
          💾 Salvar circuito como PNG
        </Botao>
      </div>
    </div>
  );
}
