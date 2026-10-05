import { IconePorta, type TipoDePorta } from '../componentes/IconePorta';
import { SeletorDeTema } from '../componentes/SeletorDeTema';
import { useAplicacao, type Tela } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { MiniCircuito } from './MiniCircuito';

interface Funcao {
  secao: string;
  icone: TipoDePorta;
  titulo: string;
  descricao: string;
  botao: string;
  destino: Tela;
}

/** As três entradas do HomeScreen, como seções de um datasheet. */
const FUNCOES: Funcao[] = [
  {
    secao: '2.1',
    icone: 'and',
    titulo: 'Expressões & Circuitos',
    descricao: 'Analise expressões lógicas, gere tabelas verdade, simplifique e visualize circuitos.',
    botao: 'Explorar',
    destino: 'principal',
  },
  {
    secao: '2.2',
    icone: 'xnor',
    titulo: 'Equivalência Lógica',
    descricao: 'Compare duas expressões e verifique se são logicamente equivalentes.',
    botao: 'Explorar',
    destino: 'equivalencia',
  },
  {
    secao: '2.3',
    icone: 'or',
    titulo: 'Problemas & Exercícios',
    descricao: 'Pratique com problemas do mundo real que podem ser resolvidos com lógica proposicional e circuitos digitais.',
    botao: 'Praticar',
    destino: 'problemas',
  },
];

/** Tela inicial (HomeScreen) no estilo datasheet. */
export function Inicio() {
  const app = useAplicacao();
  const janelas = useJanelas();

  return (
    <div className="pagina pagina--inicio">
      <header className="cabecalho-app">
        <div className="marca">
          <IconePorta tipo="and" tamanho={42} className="marca__icone" />
          <span className="marca__nome">LoZ Gates</span>
          <span className="marca__versao mono">v1.0.1</span>
        </div>
        <div className="cabecalho-app__acoes">
          <SeletorDeTema />
          <button type="button" className="botao botao--fantasma botao--pequeno" onClick={janelas.abrirManual}>
            Ajuda
          </button>
        </div>
      </header>

      <main className="inicio">
        <section className="destaque-inicio" aria-labelledby="titulo-inicio">
          <div className="destaque-inicio__texto">
            <p className="rotulo-secao">1 · Visão geral</p>
            <h1 id="titulo-inicio" className="destaque-inicio__titulo">
              Lógica proposicional e circuitos digitais, passo a passo.
            </h1>
            <p className="destaque-inicio__descricao">
              Ligue e desligue as entradas: o sinal percorre os fios e acende a saída quando a expressão é verdadeira.
            </p>
          </div>
          <MiniCircuito />
        </section>

        <section className="funcoes" aria-labelledby="titulo-funcoes">
          <h2 id="titulo-funcoes" className="rotulo-secao funcoes__titulo">
            2 · Ferramentas
          </h2>
          <ul className="funcoes__lista">
            {FUNCOES.map((funcao) => (
              <li key={funcao.secao} className="cartao-funcao">
                <div className="cartao-funcao__topo">
                  <span className="cartao-funcao__secao mono">{funcao.secao}</span>
                  <IconePorta tipo={funcao.icone} tamanho={48} className="cartao-funcao__icone" />
                </div>
                <h3 className="cartao-funcao__titulo">{funcao.titulo}</h3>
                <p className="cartao-funcao__descricao">{funcao.descricao}</p>
                <button
                  type="button"
                  className="botao botao--primario cartao-funcao__botao"
                  onClick={() => app.mostrarTela(funcao.destino)}
                  aria-label={`${funcao.botao}: ${funcao.titulo}`}
                >
                  {funcao.botao} →
                </button>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="rodape-app">
        <span>Versão 1.0.1 · Instituto de Computação · UFAL</span>
        <button type="button" className="link-discreto" onClick={() => void app.encerrarSessao()}>
          Encerrar sessão
        </button>
      </footer>
    </div>
  );
}
