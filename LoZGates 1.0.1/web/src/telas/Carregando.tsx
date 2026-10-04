interface Props {
  etapa: string;
  fracao: number;
  erro?: string | null;
  aoTentarDeNovo?: () => void;
}

/** Tela exibida enquanto o Python (Pyodide) e o pygame são carregados. */
export function Carregando({ etapa, fracao, erro, aoTentarDeNovo }: Props) {
  return (
    <main className="tela tela--estreita tela--centro carregando" aria-busy={!erro}>
      <p className="logotipo" aria-hidden="true">
        &lt;LoZ Gates&gt;
      </p>
      {erro ? (
        <div className="carregando__erro" role="alert">
          <h1 className="titulo-formulario">Não foi possível iniciar o LoZ Gates</h1>
          <p className="texto-secundario">{erro}</p>
          <p className="texto-secundario pequeno">
            Verifique a conexão com a internet (o motor Python é baixado na primeira visita) e tente de novo.
          </p>
          {aoTentarDeNovo && (
            <button type="button" className="botao botao--primario botao--normal" onClick={aoTentarDeNovo}>
              Tentar de novo
            </button>
          )}
        </div>
      ) : (
        <>
          <div
            className="barra-progresso"
            role="progressbar"
            aria-label="Carregando o LoZ Gates"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(fracao * 100)}
          >
            <span style={{ transform: `scaleX(${Math.max(0.04, fracao)})` }} />
          </div>
          <p className="texto-secundario" aria-live="polite">
            {etapa}
          </p>
        </>
      )}
    </main>
  );
}
