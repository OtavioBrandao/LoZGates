import { Botao } from '../componentes/Botao';
import { Modal } from '../componentes/Modal';

export type EscolhaCompartilhamento = 'enviar' | 'agora' | 'nunca';

const EXPLICACAO = `Seus dados de uso detalhados nos ajudam a entender melhor como melhorar o LoZ Gates.
Todos os dados são ANÔNIMOS e incluem estatísticas sobre uso de funcionalidades, padrões de interação e tipos de problemas resolvidos.
Abaixo você pode ver exatamente o que será enviado:`;

const INFORMACOES = `💡 Seus dados detalhados nos permitem:
• Identificar quais leis lógicas são mais difíceis de aplicar
• Otimizar a interface do circuito interativo
• Melhorar a detecção de erros comuns
• Personalizar a experiência de aprendizado`;

/** DetailedDataSharingDialog.show_dialog() (FrontEnd/dialogs/data_sharing_dialog.py) */
export function CompartilharDados({ preview, aoEscolher }: { preview: string; aoEscolher: (e: EscolhaCompartilhamento) => void }) {
  return (
    <Modal
      titulo="Compartilhamento de dados detalhados - LoZ Gates Beta"
      tamanho="grande"
      aoFechar={() => aoEscolher('agora')}
      rodape={
        <div className="linha-botoes linha-botoes--inicio">
          <Botao estilo="sucesso" tamanho="pequeno" onClick={() => aoEscolher('enviar')}>
            ✓&nbsp;&nbsp;Enviar Dados Detalhados (Ajudar)
          </Botao>
          <Botao estilo="aviso" tamanho="pequeno" onClick={() => aoEscolher('agora')}>
            ✕&nbsp;&nbsp;Não Agora
          </Botao>
          <Botao estilo="erro" tamanho="pequeno" onClick={() => aoEscolher('nunca')}>
            🚫&nbsp;&nbsp;Nunca Perguntar
          </Botao>
        </div>
      }
    >
      <h3 className="compartilhar__titulo">📊 Dados detalhados de uso - LoZ Gates Beta</h3>
      <p className="compartilhar__texto">{EXPLICACAO}</p>
      {preview && (
        <section className="cartao">
          <h4 className="cartao__titulo">📈 Preview dos Dados que Serão Enviados:</h4>
          <pre className="compartilhar__preview" tabIndex={0}>
            {preview}
          </pre>
        </section>
      )}
      <p className="compartilhar__texto">{INFORMACOES}</p>
    </Modal>
  );
}
