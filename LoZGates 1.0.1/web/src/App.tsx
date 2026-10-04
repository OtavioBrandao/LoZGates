import { ProvedorAplicacao, useAplicacao } from './estado/Aplicacao';
import { ProvedorJanelas } from './estado/Janelas';
import { Equivalencia } from './telas/Equivalencia';
import { Inicio } from './telas/Inicio';
import { Principal } from './telas/Principal';
import { Problemas } from './telas/Problemas';
import { ResolucaoDireta } from './telas/ResolucaoDireta';
import { SessaoEncerrada } from './telas/SessaoEncerrada';
import { SimplificacaoInterativa } from './telas/SimplificacaoInterativa';
import { TelaAbas } from './telas/TelaAbas';

export function App() {
  return (
    <ProvedorJanelas>
      <ProvedorAplicacao>
        <Telas />
      </ProvedorAplicacao>
    </ProvedorJanelas>
  );
}

/** Troca de "frames" (tkraise). As abas ficam montadas enquanto o circuito interativo existir. */
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
