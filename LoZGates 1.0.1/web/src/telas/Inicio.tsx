import { Botao } from '../componentes/Botao';
import { useAplicacao, type Tela } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';

interface Cartao {
  simbolo: string;
  titulo: string;
  descricao: string;
  botao: string;
  destino: Tela;
  largo?: boolean;
}

/** Os três cards de HomeScreen (FrontEnd/screens/home/home_screen.py). */
const CARTOES: Cartao[] = [
  {
    simbolo: '⬡',
    titulo: 'Expressões & Circuitos',
    descricao: 'Analise expressões lógicas, gere tabelas verdade,\nsimplifique e visualize circuitos.',
    botao: 'Explorar →',
    destino: 'principal',
  },
  {
    simbolo: '⟺',
    titulo: 'Equivalência Lógica',
    descricao: 'Compare duas expressões e verifique\nse são logicamente equivalentes.',
    botao: 'Explorar →',
    destino: 'equivalencia',
  },
  {
    simbolo: '⚑',
    titulo: 'Problemas & Exercícios',
    descricao:
      'Pratique com problemas do mundo real que podem ser resolvidos\ncom lógica proposicional e circuitos digitais.',
    botao: 'Praticar →',
    destino: 'problemas',
    largo: true,
  },
];

/** Tela inicial (HomeScreen). */
export function Inicio() {
  const app = useAplicacao();
  const janelas = useJanelas();

  return (
    <main className="tela tela--larga tela--inicio">
      <header className="inicio__cabecalho">
        <div>
          <h1 className="logotipo">LoZ Gates</h1>
          <p className="inicio__subtitulo">Lógica proposicional e circuitos digitais, passo a passo.</p>
        </div>
        <Botao estilo="fantasma" tamanho="pequeno" onClick={janelas.abrirManual}>
          ?&nbsp;&nbsp;Ajuda
        </Botao>
      </header>

      <nav className="inicio__cartoes" aria-label="Menu principal">
        {CARTOES.map((cartao) => (
          <article key={cartao.titulo} className={`cartao-inicio ${cartao.largo ? 'cartao-inicio--largo' : ''}`}>
            <span className="cartao-inicio__simbolo" aria-hidden="true">
              {cartao.simbolo}
            </span>
            <h2 className="cartao-inicio__titulo">{cartao.titulo}</h2>
            <p className="cartao-inicio__descricao">{cartao.descricao}</p>
            <Botao className="cartao-inicio__botao" onClick={() => app.mostrarTela(cartao.destino)} aria-label={`${cartao.botao} ${cartao.titulo}`}>
              {cartao.botao}
            </Botao>
          </article>
        ))}
      </nav>

      <footer className="inicio__rodape">
        <span>Versão 1.0.1, Instituto de Computação da UFAL</span>
        <button type="button" className="link-discreto" onClick={() => void app.encerrarSessao()}>
          Encerrar sessão
        </button>
      </footer>
    </main>
  );
}
