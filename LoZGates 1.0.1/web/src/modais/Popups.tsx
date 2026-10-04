import { Botao } from '../componentes/Botao';
import { Modal } from '../componentes/Modal';

/** popup_erro() — também usado pelo desktop para avisos como "Imagem salva com sucesso!" */
export function PopupErro({ mensagem, aoFechar, titulo = 'Erro' }: { mensagem: string; aoFechar: () => void; titulo?: string }) {
  return (
    <Modal
      titulo={titulo}
      tamanho="pequeno"
      aoFechar={aoFechar}
      classe="popup-erro"
      rodape={
        <Botao estilo="cor" tamanho="pequeno" cor="#7A2020" corHover="#9A2A2A" corTexto="#FFFFFF" onClick={aoFechar} autoFocus>
          OK
        </Botao>
      }
    >
      <p className="popup-erro__mensagem">{mensagem.trim()}</p>
    </Modal>
  );
}

const INFO_EXTRA =
  '\n\nLoZ Gates - Ajuda\nEste aplicativo permite criar, visualizar e simplificar expressões de lógica proposicional.\nUse as abas para acessar circuitos, expressões e problemas reais.';

/** popup_duvida() — botão ❓ da aba Circuito */
export function PopupDuvida({ mensagem, aoFechar }: { mensagem: string; aoFechar: () => void }) {
  return (
    <Modal titulo="Ajuda" tamanho="medio" aoFechar={aoFechar}>
      <pre className="texto-pre">{(INFO_EXTRA + mensagem).trim()}</pre>
    </Modal>
  );
}
