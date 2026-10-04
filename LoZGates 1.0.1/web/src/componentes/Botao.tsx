import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from 'react';

type Estilo = 'primario' | 'sucesso' | 'aviso' | 'erro' | 'voltar' | 'fantasma' | 'lei' | 'cor';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  estilo?: Estilo;
  tamanho?: 'normal' | 'pequeno' | 'largo';
  /** Para estilo="cor": fundo e hover (ex.: botões de modo do circuito interativo) */
  cor?: string;
  corHover?: string;
  corTexto?: string;
  children: ReactNode;
}

/**
 * Botões padronizados — equivalem às fábricas de FrontEnd/components/buttons.py:
 *   botao_padrao (primario/sucesso/aviso/erro), botao_voltar ("← " + nome),
 *   botao_ghost (fantasma), botao_lei e botao_especial (cor).
 */
export function Botao({ estilo = 'primario', tamanho = 'normal', cor, corHover, corTexto, className = '', style, children, ...resto }: Props) {
  const variaveis: CSSProperties = { ...style };
  if (cor) (variaveis as Record<string, string>)['--botao-fundo'] = cor;
  if (corHover) (variaveis as Record<string, string>)['--botao-hover'] = corHover;
  if (corTexto) (variaveis as Record<string, string>)['--botao-texto'] = corTexto;
  return (
    <button type="button" className={`botao botao--${estilo} botao--${tamanho} ${className}`} style={variaveis} {...resto}>
      {estilo === 'voltar' ? <>← {children}</> : children}
    </button>
  );
}

/** Escurece uma cor para o hover (CircuitModeSelector._darken_color). */
export function escurecer(hex: string): string {
  const limpo = hex.replace('#', '');
  const canais = [0, 2, 4].map((i) => Math.max(0, Math.floor(parseInt(limpo.slice(i, i + 2), 16) * 0.7)));
  return `#${canais.map((c) => c.toString(16).padStart(2, '0')).join('')}`;
}
