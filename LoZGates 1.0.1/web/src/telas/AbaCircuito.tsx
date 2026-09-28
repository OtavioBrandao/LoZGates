import { useState } from 'react';
import { Botao } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { textos } from '../motor/textos';

/** Aba "Circuito": imagem gerada por BackEnd/principal.plotar_circuito_logico (pygame) */
export function AbaCircuito() {
  const app = useAplicacao();
  const janelas = useJanelas();
  const [tamanhoReal, setTamanhoReal] = useState(false);

  // salvar_imagem(): salva o circuito.png original (sem a borda)
  const salvarImagem = () => {
    if (!app.imagem) {
      janelas.popupErro('Imagem não encontrada.');
      return;
    }
    const link = document.createElement('a');
    link.href = app.imagem.original;
    link.download = 'circuito.png';
    document.body.appendChild(link);
    link.click();
    link.remove();
    janelas.popupErro('Imagem salva com sucesso!', 'LoZ Gates');
  };

  return (
    <div className="aba-circuito">
      <div className="aba-circuito__barra">
        <p className="texto-secundario">
          Clique na imagem para alternar entre caber na tela e ver em tamanho real.
        </p>
        <button
          type="button"
          className="botao-duvida"
          aria-label="Ajuda rápida sobre circuitos"
          onClick={() => janelas.popupDuvida(textos().duvida_circuitos)}
        >
          ❓
        </button>
      </div>

      <figure className={`aba-circuito__figura ${tamanhoReal ? 'aba-circuito__figura--real' : ''}`}>
        {app.imagem ? (
          <button type="button" className="aba-circuito__imagem" onClick={() => setTamanhoReal((v) => !v)} aria-pressed={tamanhoReal}>
            <img
              src={app.imagem.src}
              width={app.imagem.largura}
              height={app.imagem.altura}
              alt={`Circuito lógico gerado para ${app.labelCircuito.replace('Expressão Lógica Proposicional: ', '')}`}
            />
          </button>
        ) : (
          <figcaption className="texto-secundario">{app.textoImagem}</figcaption>
        )}
      </figure>

      <div className="linha-botoes">
        <Botao onClick={salvarImagem}>💾 Salvar circuito como PNG</Botao>
      </div>
    </div>
  );
}
