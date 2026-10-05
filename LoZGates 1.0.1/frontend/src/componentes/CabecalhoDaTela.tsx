import type { ReactNode } from 'react';
import { Botao } from './Botao';
import { SeletorDeTema } from './SeletorDeTema';

interface Props {
  /** Rótulo de seção no estilo datasheet, ex.: "2.1 · Expressões & Circuitos" */
  secao: string;
  titulo: ReactNode;
  /** Sem ele não há Voltar no cabeçalho (a tela tem o seu, como a simplificação interativa) */
  aoVoltar?: () => void;
  voltarDesabilitado?: boolean;
}

/** Cabeçalho das telas internas: Voltar, a seção e o título, e o tema. */
export function CabecalhoDaTela({ secao, titulo, aoVoltar, voltarDesabilitado }: Props) {
  return (
    <header className="cabecalho-expressao">
      {aoVoltar && (
        <Botao estilo="voltar" tamanho="pequeno" onClick={aoVoltar} disabled={voltarDesabilitado}>
          Voltar
        </Botao>
      )}
      <div className="cabecalho-expressao__texto">
        <span className="rotulo-secao">{secao}</span>
        <h1 className="cabecalho-tela__titulo">{titulo}</h1>
      </div>
      <SeletorDeTema />
    </header>
  );
}
