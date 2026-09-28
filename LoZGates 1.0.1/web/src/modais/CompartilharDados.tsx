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

/** DetailedDataSharingDialog.show_dialog() (FrontEnd/logging_system.py) */
export function CompartilharDados({ preview, aoEscolher }: { preview: string; aoEscolher: (e: EscolhaCompartilhamento) => void }) {
  return (
    <Modal
      titulo="Compartilhamento de dados detalhados - LoZ Gates Beta"
      tamanho="grande"
      aoFechar={() => aoEscolher('agora')}
      rodape={
        <div className="linha-botoes linha-botoes--inicio">
          <Botao estilo="cor" cor="#4CAF50" corHover="#3E9142" corTexto="#FFFFFF" onClick={() => aoEscolher('enviar')}>
            ✅ Enviar Dados Detalhados (Ajudar)
          </Botao>
          <Botao estilo="cor" cor="#FF9800" corHover="#D98200" corTexto="#FFFFFF" onClick={() => aoEscolher('agora')}>
            ❌ Não Agora
          </Botao>
          <Botao estilo="cor" cor="#F44336" corHover="#C9372C" corTexto="#FFFFFF" onClick={() => aoEscolher('nunca')}>
            🚫 Nunca Perguntar
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
