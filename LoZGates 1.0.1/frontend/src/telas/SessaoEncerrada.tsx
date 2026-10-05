import { Botao } from '../componentes/Botao';

/** Depois de on_closing(): no desktop a janela fechava. */
export function SessaoEncerrada() {
  return (
    <main className="tela tela--estreita tela--centro">
      <p className="logotipo logotipo--pequeno" aria-hidden="true">
        &lt;LoZ Gates&gt;
      </p>
      <h1 className="titulo-formulario">Sessão encerrada</h1>
      <p className="texto-secundario">🚀 Obrigado por usar o LoZ Gates!</p>
      <div className="pilha-botoes">
        <Botao onClick={() => window.location.reload()}>Iniciar nova sessão</Botao>
      </div>
    </main>
  );
}
