# LoZ Gates — Design System

> Etapa 8: Redesign Visual & UX  
> Versão 1.0 | Setembro 2026

---

## Princípios de Design

| Princípio | Descrição |
|---|---|
| **Clareza** | O aluno deve saber em todo momento: onde está, o que está fazendo, o que aconteceu |
| **Hierarquia** | Elementos importantes têm maior peso visual. Ações primárias se destacam. |
| **Consistência** | Todos os elementos usam os mesmos tokens. Sem cores ou fontes hardcoded. |
| **Pedagogia** | A interface serve o aprendizado. Feedback claro, progressão visível. |
| **Moderação** | Sem neons, sem excessos. Profissional, não infantil. |

---

## Paleta de Cores

### Backgrounds

| Token | Valor | Uso |
|---|---|---|
| `PRIMARY_BG` | `#0E0F14` | Fundo principal da janela |
| `SECONDARY_BG` | `#151720` | Fundo de seções, tabs |
| `SURFACE_DARK` | `#1C1E2B` | Cards principais |
| `SURFACE_MEDIUM` | `#232638` | Surface elevada dentro de cards |
| `SURFACE_LIGHT` | `#2A2D3E` | Campos de entrada, itens de lista |

### Cores de Ação

| Token | Valor | Uso |
|---|---|---|
| `PRIMARY` | `#5B8AF0` | Ação principal (Confirmar, Comparar) |
| `PRIMARY_HOVER` | `#7BA0F5` | Hover de ação principal |
| `PRIMARY_MUTED` | `#1E2D5A` | Fundo de badge/chip primário |

### Estados

| Token | Valor | Uso |
|---|---|---|
| `SUCCESS` | `#3EAE6E` | Ações positivas, resposta correta |
| `SUCCESS_MUTED` | `#1A3D2E` | Fundo de área de sucesso |
| `WARNING` | `#E8A838` | Atenção, avisos, Desfazer |
| `WARNING_MUTED` | `#3D2F10` | Fundo de área de aviso |
| `ERROR` | `#E05252` | Erro, Parar circuito |
| `ERROR_MUTED` | `#3D1515` | Fundo de área de erro |

### Accent

| Token | Valor | Uso |
|---|---|---|
| `ACCENT_LOGIC` | `#C678DD` | Roxo para elementos de lógica |
| `ACCENT_PURPLE` | `#C678DD` | Alias semântico de ACCENT_LOGIC |

### Texto

| Token | Valor | Uso |
|---|---|---|
| `TEXT_PRIMARY` | `#EAEDF5` | Texto principal |
| `TEXT_SECONDARY` | `#8A90A8` | Texto secundário / auxiliar |
| `TEXT_MUTED` | `#565A72` | Placeholders |
| `TEXT_ACCENT` | `#7AABFF` | Labels de seção, destaques |
| `TEXT_CODE` | `#A8D5FF` | Expressões lógicas em destaque |

### Bordas

| Token | Valor | Uso |
|---|---|---|
| `BORDER_DEFAULT` | `#2C2F42` | Bordas sutis de cards |
| `BORDER_ACTIVE` | `#5B8AF0` | Borda de foco / seleção ativa |
| `BORDER_ACCENT` | `#3A4A7A` | Borda com destaque médio |

---

## Tipografia

| Token | Família | Tamanho | Peso | Uso |
|---|---|---|---|---|
| `SIZE_DISPLAY` | Momentz | 32 | bold | Logo "LoZ Gates" na Home |
| `SIZE_TITLE_LARGE` | Segoe UI | 22 | bold | Título de tela |
| `SIZE_TITLE_MEDIUM` | Segoe UI | 20 | bold | Título de seção |
| `SIZE_TITLE_SMALL` | Segoe UI | 18 | bold | Subtítulo de card |
| `SIZE_SUBTITLE` | Segoe UI | 16 | bold | Subtítulo secundário |
| `SIZE_BODY` | Segoe UI | 14 | normal/bold | Texto padrão |
| `SIZE_BODY_SMALL` | Segoe UI | 13 | normal | Texto auxiliar |
| `SIZE_CAPTION` | Segoe UI | 12 | normal | Labels pequenos |
| `SIZE_CODE` | Consolas | 14 | normal | Expressões lógicas |
| `SIZE_CODE_LARGE` | Consolas | 18 | bold | Expressão principal em destaque |

**Funções helper disponíveis:**
```python
get_font(size, weight)        # Segoe UI
get_title_font(size)          # Segoe UI bold
get_code_font(size, weight)   # Consolas (para expressões lógicas)
```

---

## Espaçamento

| Token | Valor | Uso |
|---|---|---|
| `XS = 4` | 4px | Micro-espaçamentos entre elementos |
| `SM = 8` | 8px | Entre elementos relacionados |
| `MD = 12` | 12px | Padding interno de componentes |
| `LG = 16` | 16px | Entre seções menores |
| `XL = 24` | 24px | Padding de cards |
| `XXL = 32` | 32px | Entre seções maiores |
| `XXXL = 48` | 48px | Margens de tela |

---

## Border Radius

| Token | Valor | Uso |
|---|---|---|
| `CORNER_RADIUS_SMALL = 6` | 6px | Inputs, badges, chips |
| `CORNER_RADIUS_MEDIUM = 10` | 10px | Botões, cards internos |
| `CORNER_RADIUS_LARGE = 14` | 14px | Cards principais |
| `CORNER_RADIUS_XL = 20` | 20px | Containers grandes, home cards |

---

## Botões — Variantes

### Hierarquia Visual

```
PRIMARY (Azul)    > SUCCESS (Verde)  > WARNING (Âmbar)
Ação principal      Ação positiva      Ação reversível

DANGER (Vermelho) > GHOST (Sem fundo)
Ação destrutiva     Ação secundária

LAW (Surface)
Botões de leis — sempre habilitados (regra pedagógica)
```

### Variantes da classe Button

| Variante | fg_color | hover_color | Uso |
|---|---|---|---|
| `botao_padrao(style="primary")` | PRIMARY | PRIMARY_HOVER | Ação principal |
| `botao_padrao(style="success")` | SUCCESS | SUCCESS_HOVER | Verificar, Confirmar |
| `botao_padrao(style="warning")` | WARNING | escurecido | Desfazer |
| `botao_padrao(style="error")` | ERROR | ERROR_HOVER | Parar, ação destrutiva |
| `botao_ghost()` | transparent | SURFACE_MEDIUM | Voltar (secundário) |
| `botao_lei()` | SURFACE_DARK | SURFACE_MEDIUM | 9 leis do Resolver |

---

## Padrões de Feedback

### Dentro da interface (labels)

| Tipo | Ícone | Cor de texto | Cor de fundo |
|---|---|---|---|
| Sucesso | ✓ | `TEXT_SUCCESS` | `SUCCESS_MUTED` |
| Erro | ✕ | `TEXT_ERROR` | `ERROR_MUTED` |
| Aviso | ! | `TEXT_WARNING` | `WARNING_MUTED` |
| Info | i | `TEXT_ACCENT` | `SURFACE_MEDIUM` |

> **Regra:** Nunca use apenas cor para indicar estado. Use sempre ícone + texto + cor.

### Popups

- Usar `CTkToplevel` com `fg_color=SURFACE_DARK`
- Fonte: `get_font(SIZE_BODY)`
- Botão OK: `botao_ghost()` para pop de info, `botao_padrao(style="error")` para erros

---

## Padrões de Cards

### Card de Tela (tela-card)

```python
ctk.CTkFrame(
    parent,
    fg_color=Colors.SURFACE_DARK,
    border_width=Dimensions.BORDER_WIDTH_STANDARD,
    border_color=Colors.BORDER_DEFAULT,
    corner_radius=Dimensions.CORNER_RADIUS_XL,
)
```

### Card de Funcionalidade (home-card)

```python
# Usa corner_radius=CORNER_RADIUS_LARGE
# Tem hover: bind <Enter>/<Leave> para mudar border_color
# Contém: ícone + título + descrição + botão de ação
```

### Card de Passo (step-card)

```python
# Para histórico do Resolver
# Ícone de status: ✓ (sucesso) ou → (em andamento)
# fg_color=SURFACE_MEDIUM com border esquerda colorida
```

### Card de Seção (section-card)

```python
ctk.CTkFrame(
    parent,
    fg_color=Colors.SURFACE_MEDIUM,
    corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
)
```

---

## Navegação

- Cada tela tem um header com nome da tela atual
- Botão "← Voltar" usa variante `ghost` (sem cor de fundo)
- Navegação via `NavigationController.show_screen(name)` — não alterar

---

## Acessibilidade

1. **Não depender só de cor** — sempre usar ícone + texto + cor
2. **Tamanho mínimo de texto** — 12px (SIZE_CAPTION)
3. **Área mínima de clique** — 44px de altura para botões
4. **Contraste** — TEXT_PRIMARY (#EAEDF5) sobre SURFACE_DARK (#1C1E2B) = 11.5:1 ✓
5. **Focus visual** — BORDER_ACTIVE (#5B8AF0) visível em todos os estados

---

## O Que NÃO Fazer

- ❌ Cores hardcoded fora dos tokens
- ❌ `state="disabled"` nos 9 botões de lei do Resolver (regra pedagógica)
- ❌ Depender apenas de cor para indicar sucesso/erro
- ❌ Animações que bloqueiam o event loop do Tkinter
- ❌ Alterar lógica de controllers, states ou backend
- ❌ Criar novo arquivo de configuração de tema separado
