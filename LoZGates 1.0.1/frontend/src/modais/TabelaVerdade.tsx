import { Botao } from '../componentes/Botao';
import { Modal } from '../componentes/Modal';

export interface DadosTabela {
  titulo: string;
  colunas: string[];
  tabela: number[][];
  conclusao: string;
  cor_conclusao: 'sucesso' | 'erro' | 'info';
}

/** exibir_tabela_verdade() — janela "Tabela Verdade" */
export function TabelaVerdade({ dados, aoFechar }: { dados: DadosTabela; aoFechar: () => void }) {
  const ultima = dados.colunas.length - 1;
  return (
    <Modal
      titulo="Tabela Verdade"
      tamanho="grande"
      aoFechar={aoFechar}
      rodape={
        <Botao onClick={aoFechar} autoFocus>
          Fechar
        </Botao>
      }
    >
      <h3 className="tabela-verdade__titulo">{dados.titulo}</h3>
      <div className="tabela-verdade__rolagem" tabIndex={0} aria-label="Tabela verdade (role para ver todas as colunas)">
        <table className="tabela-verdade">
          <thead>
            <tr>
              {dados.colunas.map((coluna, i) => (
                <th key={i} scope="col" className={i === ultima ? 'tabela-verdade__final' : undefined}>
                  {coluna}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dados.tabela.map((linha, i) => (
              <tr key={i}>
                {linha.map((valor, j) => (
                  <td key={j} className={`${valor ? 'valor-1' : 'valor-0'} ${j === ultima ? 'tabela-verdade__final' : ''}`}>
                    {valor}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className={`tabela-verdade__conclusao cor-${dados.cor_conclusao}`}>{dados.conclusao}</p>
    </Modal>
  );
}
