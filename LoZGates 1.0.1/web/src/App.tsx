import { useCallback, useEffect, useState } from 'react';
import { ProvedorAplicacao, useAplicacao } from './estado/Aplicacao';
import { ProvedorJanelas } from './estado/Janelas';
import { carregarMotor } from './motor/pyodide';
import { Carregando } from './telas/Carregando';
import { Equivalencia } from './telas/Equivalencia';
import { Inicio } from './telas/Inicio';
import { Principal } from './telas/Principal';
import { Problemas } from './telas/Problemas';
import { ResolucaoDireta } from './telas/ResolucaoDireta';
import { SessaoEncerrada } from './telas/SessaoEncerrada';
import { SimplificacaoInterativa } from './telas/SimplificacaoInterativa';
import { TelaAbas } from './telas/TelaAbas';

export function App() {
  const [pronto, setPronto] = useState(false);
  const [progresso, setProgresso] = useState({ etapa: 'Preparando…', fracao: 0 });
  const [erro, setErro] = useState<string | null>(null);

  const carregar = useCallback(() => {
    setErro(null);
    carregarMotor((etapa, fracao) => setProgresso({ etapa, fracao }))
      .then(() => setPronto(true))
      .catch((e: unknown) => {
        console.error(e);
        setErro(e instanceof Error ? e.message : String(e));
      });
  }, []);

  useEffect(carregar, [carregar]);

  if (!pronto) return <Carregando etapa={progresso.etapa} fracao={progresso.fracao} erro={erro} aoTentarDeNovo={carregar} />;

  return (
    <ProvedorJanelas>
      <ProvedorAplicacao>
        <Telas />
      </ProvedorAplicacao>
    </ProvedorJanelas>
  );
}

/** Troca de "frames" (show_frame). As abas ficam montadas enquanto o circuito interativo existir. */
function Telas() {
  const app = useAplicacao();
  const abasMontadas = ['abas', 'resolucao', 'interativo'].includes(app.tela) || app.seletor > 0;

  return (
    <div className={`aplicacao ${app.ocupado ? 'aplicacao--ocupada' : ''}`}>
      {app.ocupado && <div className="indicador-ocupado" aria-hidden="true" />}
      {app.tela === 'inicio' && <Inicio />}
      {app.tela === 'principal' && <Principal />}
      {app.tela === 'equivalencia' && <Equivalencia />}
      {app.tela === 'problemas' && <Problemas />}
      {abasMontadas && <TelaAbas oculta={app.tela !== 'abas'} />}
      {app.tela === 'resolucao' && <ResolucaoDireta />}
      {app.tela === 'interativo' && <SimplificacaoInterativa key={app.sessaoInterativa} />}
      {app.tela === 'encerrada' && <SessaoEncerrada />}
    </div>
  );
}
