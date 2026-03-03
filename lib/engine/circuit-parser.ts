// Porte de parser.py - Parser de expressao booleana para AST de circuito
import type { CircuitNode, VariableNode, OperatorNode, CircuitLayout } from "./types"

function createVariable(name: string): VariableNode {
  return { type: "variable", name }
}

function createOperator(op: string, children: CircuitNode[]): OperatorNode {
  return { type: "operator", op, children }
}

export function parseCircuitExpression(expression: string): CircuitNode {
  const tokens = expression.replace(/\s/g, "").split("")
  let pos = 0

  function peek(): string | null {
    return pos < tokens.length ? tokens[pos] : null
  }

  function consume(): string {
    return tokens[pos++]
  }

  function parseFactor(): CircuitNode {
    const token = peek()
    if (token && /[a-zA-Z]/.test(token)) {
      return createVariable(consume())
    }
    if (token === "~") {
      consume()
      if (peek() === "(") {
        consume() // '('
        const expr = parseExpression()
        consume() // ')'
        return createOperator("~", [expr])
      }
      return createOperator("~", [parseFactor()])
    }
    if (token === "(") {
      consume() // '('
      const expr = parseExpression()
      consume() // ')'
      return expr
    }
    throw new Error("Certifique-se de que os parenteses estejam sendo fechados.")
  }

  function parseTerm(): CircuitNode {
    let node = parseFactor()
    while (peek() === "*") {
      const op = consume()
      const right = parseFactor()
      node = createOperator(op, [node, right])
    }
    return node
  }

  function parseExpression(): CircuitNode {
    let node = parseTerm()
    while (peek() === "+") {
      const op = consume()
      const right = parseTerm()
      node = createOperator(op, [node, right])
    }
    return node
  }

  return parseExpression()
}

export function calculateDynamicLayout(node: CircuitNode, yBase = 0): CircuitLayout {
  if (node.type === "variable") {
    return { type: "variable", name: node.name, yPos: yBase, height: 80, width: 0 }
  }

  if (node.type === "operator" && node.op === "~" && node.children[0].type === "variable") {
    return { type: "negated_variable", name: node.children[0].name, yPos: yBase, height: 80, width: 0 }
  }

  if (node.type === "operator") {
    const childLayouts: CircuitLayout[] = []
    let currentY = yBase
    let maxWidth = 0

    for (const child of node.children) {
      const childLayout = calculateDynamicLayout(child, currentY)
      childLayouts.push(childLayout)
      currentY += childLayout.height + 20
      maxWidth = Math.max(maxWidth, childLayout.width)
    }

    const totalHeight = currentY - yBase - 20

    return {
      type: "gate",
      op: node.op,
      yPos: yBase + totalHeight / 2,
      height: totalHeight,
      width: maxWidth + 180,
      children: childLayouts,
    }
  }

  return { type: "variable", yPos: yBase, height: 80, width: 0 }
}

export function collectVariables(node: CircuitNode): Set<string> {
  if (node.type === "variable") return new Set([node.name])
  if (node.type === "operator") {
    const vars = new Set<string>()
    for (const child of node.children) {
      collectVariables(child).forEach((v) => vars.add(v))
    }
    return vars
  }
  return new Set()
}
