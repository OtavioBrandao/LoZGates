import { Botao } from '../componentes/Botao';
import { Modal } from '../componentes/Modal';

/** popup_erro() — o desktop também o usava para avisos como "Imagem salva com sucesso!" */
export function PopupErro({ mensagem, aoFechar, titulo = 'Erro' }: { mensagem: string; aoFechar: () => void; titulo?: string }) {
  return (
    <Modal
      titulo={titulo}
      tamanho="pequeno"
      aoFechar={aoFechar}
      classe="popup-erro"
      rodape={
        <Botao estilo="erro" tamanho="pequeno" onClick={aoFechar} autoFocus>
          OK
        </Botao>
      }
    >
      {titulo === 'Erro' && (
        <p className="popup-erro__icone" aria-hidden="true">
          ✕
        </p>
      )}
      <p className="popup-erro__mensagem">{mensagem.trim()}</p>
    </Modal>
  );
}

const INFO_EXTRA = 'LoZ Gates — Ferramenta educacional para Lógica Proposicional e Circuitos Digitais.\n\n';

/** popup_duvida() — botão "?" da aba Circuito */
export function PopupDuvida({ mensagem, aoFechar }: { mensagem: string; aoFechar: () => void }) {
  return (
    <Modal
      titulo="?   Ajuda"
      tamanho="medio"
      aoFechar={aoFechar}
      rodape={
        <Botao estilo="fantasma" tamanho="pequeno" onClick={aoFechar} autoFocus>
          Fechar
        </Botao>
      }
    >
      <pre className="texto-pre">{INFO_EXTRA + mensagem.trim()}</pre>
    </Modal>
  );
}
