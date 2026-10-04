import { Botao } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';

/** frame_inicio */
export function Inicio() {
  const app = useAplicacao();
  const janelas = useJanelas();

  return (
    <main className="tela tela--inicio">
      <div className="inicio">
        <h1 className="logotipo" aria-label="LoZ Gates">
          &lt;LoZ Gates&gt;
        </h1>
        <p className="inicio__subtitulo">Lógica Proposicional, Álgebra Booleana e Circuitos Digitais</p>

        <nav className="inicio__menu" aria-label="Menu principal">
          <svg className="inicio__trilha" viewBox="0 0 40 300" preserveAspectRatio="none" aria-hidden="true">
            <path className="inicio__barramento" d="M20 0 V300" />
            <path className="inicio__ramal" d="M20 50 H40" />
            <path className="inicio__ramal" d="M20 150 H40" />
            <path className="inicio__ramal" d="M20 250 H40" />
            <circle cx="20" cy="50" r="3.5" />
            <circle cx="20" cy="150" r="3.5" />
            <circle cx="20" cy="250" r="3.5" />
          </svg>
          <ul className="inicio__botoes">
            <li>
              <Botao tamanho="largo" onClick={() => app.mostrarTela('principal')}>
                💡Circuitos e Expressões
              </Botao>
            </li>
            <li>
              <Botao tamanho="largo" onClick={() => app.mostrarTela('equivalencia')}>
                🔄Equivalência Lógica
              </Botao>
            </li>
            <li>
              <Botao tamanho="largo" onClick={janelas.abrirManual}>
                ❔Ajuda
              </Botao>
            </li>
          </ul>
        </nav>
      </div>

      <footer className="inicio__rodape">
        <span>Versão 1.0.1, Instituto de Computação da UFAL</span>
        <button type="button" className="link-discreto" onClick={() => void app.encerrarSessao()}>
          Encerrar sessão
        </button>
      </footer>
    </main>
  );
}
