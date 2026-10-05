import type { ReactNode } from 'react';
import { Botao } from './Botao';

interface Props {
  titulo?: ReactNode;
  voltar?: { rotulo?: string; acao: () => void };
  extra?: ReactNode;
}

/** Cabeçalho das telas: botão de voltar (dourado, como botao_voltar) + título. */
export function TopoTela({ titulo, voltar, extra }: Props) {
  return (
    <header className="topo-tela">
      {voltar && (
        <Botao estilo="voltar" tamanho="pequeno" onClick={voltar.acao} className="topo-tela__voltar">
          {voltar.rotulo ?? 'Voltar'}
        </Botao>
      )}
      {titulo && <h1 className="topo-tela__titulo">{titulo}</h1>}
      {extra && <div className="topo-tela__extra">{extra}</div>}
    </header>
  );
}
