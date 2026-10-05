import { useId, useState } from 'react';
import { Abas } from '../componentes/Abas';
import { Botao } from '../componentes/Botao';
import { Modal } from '../componentes/Modal';
import { ABAS_MANUAL, type Bloco } from '../dados/manual';

/** show_interactive_help() — "📚 LoZ Gates - manual interativo" */
export function ManualInterativo({ aoFechar }: { aoFechar: () => void }) {
  const [aba, setAba] = useState(ABAS_MANUAL[0].id);
  const idBase = useId();
  const atual = ABAS_MANUAL.find((a) => a.id === aba)!;

  return (
    <Modal titulo="📚 LoZ Gates - manual interativo" tamanho="grande" aoFechar={aoFechar} classe="manual">
      <header className="manual__cabecalho">
        <p className="manual__titulo">🚀 LoZ Gates - manual completo</p>
        <p className="manual__subtitulo">Ferramenta educacional para Lógica Proposicional &amp; Circuitos Digitais</p>
      </header>
      <Abas
        idBase={idBase}
        variante="manual"
        rotulo="Seções do manual"
        abas={ABAS_MANUAL.map((a) => ({ id: a.id, rotulo: a.rotulo }))}
        atual={aba}
        aoMudar={setAba}
      />
      <div
        className="manual__painel"
        role="tabpanel"
        id={`${idBase}-painel-${aba}`}
        aria-labelledby={`${idBase}-aba-${aba}`}
        tabIndex={0}
        key={aba}
      >
        {atual.blocos.map((bloco, i) => (
          <BlocoManual key={i} bloco={bloco} aoFechar={aoFechar} />
        ))}
      </div>
    </Modal>
  );
}

function BlocoManual({ bloco, aoFechar }: { bloco: Bloco; aoFechar: () => void }) {
  switch (bloco.tipo) {
    case 'titulo':
      return <h3 className="manual__secao">{bloco.texto}</h3>;
    case 'paragrafo':
      return <p className="manual__paragrafo">{bloco.texto}</p>;
    case 'lista':
      return (
        <ul className="manual__lista">
          {bloco.itens.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      );
    case 'codigo':
      return <pre className="manual__codigo">{bloco.texto}</pre>;
    case 'operador':
      return (
        <article className="cartao manual__operador">
          <h4>{bloco.nome}</h4>
          <dl>
            <dt>Símbolo:</dt>
            <dd className="mono">{bloco.simbolo}</dd>
            <dt>Exemplo:</dt>
            <dd className="mono">{bloco.exemplo}</dd>
            <dt>Significado:</dt>
            <dd>{bloco.significado}</dd>
          </dl>
        </article>
      );
    case 'funcionalidade':
      return (
        <article className="cartao">
          <h4 className="cartao__titulo">{bloco.titulo}</h4>
          <p className="texto-secundario">{bloco.descricao}</p>
          <ul className="manual__detalhes">
            {bloco.detalhes.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </article>
      );
    case 'exemplos':
      return (
        <article className="cartao">
          <h4 className={`cartao__titulo cor-${bloco.cor}`}>{bloco.nivel}</h4>
          <ul className="manual__exemplos">
            {bloco.exemplos.map(([expressao, descricao]) => (
              <li key={expressao}>
                <code className="mono destaque">{expressao}</code>
                <span className="texto-secundario">→ {descricao}</span>
              </li>
            ))}
          </ul>
        </article>
      );
    case 'lei':
      return (
        <article className="cartao">
          <h4 className="cartao__titulo">{bloco.nome}</h4>
          <ul className="manual__regras">
            {bloco.regras.map((r) => (
              <li key={r} className="mono">
                • {r}
              </li>
            ))}
          </ul>
          <p className="texto-secundario manual__paragrafo">{bloco.explicacao}</p>
        </article>
      );
    case 'controles':
      return (
        <section>
          <h3 className="manual__secao">{bloco.titulo}</h3>
          <dl className="cartao manual__controles">
            {bloco.controles.map(([tecla, descricao]) => (
              <div key={tecla}>
                <dt>
                  <kbd>{tecla}</kbd>
                </dt>
                <dd>{descricao}</dd>
              </div>
            ))}
          </dl>
        </section>
      );
    case 'dicas':
      return (
        <article className="cartao">
          <h4 className="cartao__titulo">
            {bloco.icone} {bloco.titulo}
          </h4>
          <ul className="manual__dicas">
            {bloco.dicas.map((d) => (
              <li key={d}>💡 {d}</li>
            ))}
          </ul>
        </article>
      );
    case 'botoes':
      return (
        <div className="linha-botoes linha-botoes--inicio">
          {bloco.botoes.map((b) => (
            <Botao
              key={b.texto}
              estilo="cor"
              tamanho="pequeno"
              cor={b.cor || '#1A9AB0'}
              corHover="#1976D2"
              corTexto="#FFFFFF"
              onClick={() => (b.acao === 'fechar' ? aoFechar() : window.open(b.url, '_blank', 'noopener'))}
            >
              {b.texto}
            </Botao>
          ))}
        </div>
      );
    case 'destaque':
      return <blockquote className="manual__destaque">{bloco.texto}</blockquote>;
  }
}
