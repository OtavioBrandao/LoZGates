// Expression Tree - Node class and tree builder
// Ported from Python identificar_lei.py

export class ExprNode {
  valor: string
  esquerda: ExprNode | null
  direita: ExprNode | null

  constructor(valor: string, esquerda: ExprNode | null = null, direita: ExprNode | null = null) {
    this.valor = valor
    this.esquerda = esquerda
    this.direita = direita
  }

  toString(): string {
    if (this.valor === "&" || this.valor === "|") {
      return `(${this.esquerda}${this.valor}${this.direita})`
    } else if (this.valor === "!") {
      return `!${this.esquerda}`
    }
    return this.valor
  }

  getSize(): number {
    let size = 1
    if (this.esquerda) size += this.esquerda.getSize()
    if (this.direita) size += this.direita.getSize()
    return size
  }

  clone(): ExprNode {
    return new ExprNode(
      this.valor,
      this.esquerda ? this.esquerda.clone() : null,
      this.direita ? this.direita.clone() : null
    )
  }
}

export function buildTree(expr: string): ExprNode {
  expr = expr.replace(/\s/g, "")

  function parseOr(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      const c = s[i]
      if (c === ")") depth++
      else if (c === "(") depth--
      else if (c === "|" && depth === 0) {
        return new ExprNode("|", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      const c = s[i]
      if (c === ")") depth++
      else if (c === "(") depth--
      else if (c === "&" && depth === 0) {
        return new ExprNode("&", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): ExprNode {
    if (s.startsWith("!")) {
      return new ExprNode("!", parseOr(s.slice(1)))
    } else if (s.startsWith("(") && s.endsWith(")")) {
      return parseOr(s.slice(1, -1))
    }
    return new ExprNode(s)
  }

  return parseOr(expr)
}

// Build tree from Boolean algebra (using *, +, ~)
export function buildBooleanTree(expr: string): ExprNode {
  expr = expr.replace(/\s/g, "")

  function parseOr(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      const c = s[i]
      if (c === ")") depth++
      else if (c === "(") depth--
      else if (c === "+" && depth === 0) {
        return new ExprNode("+", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      const c = s[i]
      if (c === ")") depth++
      else if (c === "(") depth--
      else if (c === "*" && depth === 0) {
        return new ExprNode("*", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): ExprNode {
    if (s.startsWith("~")) {
      return new ExprNode("~", parseOr(s.slice(1)))
    } else if (s.startsWith("(") && s.endsWith(")")) {
      return parseOr(s.slice(1, -1))
    }
    return new ExprNode(s)
  }

  return parseOr(expr)
}
