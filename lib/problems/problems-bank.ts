// Problems Bank - 30 real-world problems
// Ported from Python problems_bank.py

export interface Problem {
  name: string
  question: string
  answer: string
  difficulty: "Facil" | "Medio" | "Dificil" | "Supremo"
}

export const PROBLEMS_BANK: Problem[] = [
  {
    name: "Airbags",
    question:
      "Larissa e uma engenheira de software muito dedicada. Em um de seus trabalhos na empresa automobilistica, lhe foi confiado o desenvolvimento de um circuito logico para o sistema de airbags dos carros da empresa. O circuito so deve ser ativado sob as seguintes condicoes: O veiculo deve estar em movimento (V), o passageiro deve estar no carro (P) e o sensor de impacto deve estar ativado (I). Qual e a expressao que representa esse sistema?",
    answer: "(V & P & I)",
    difficulty: "Facil",
  },
  {
    name: "Sem mais acidentes",
    question:
      "Nos anos 3000 o sistema de transporte mundial foi impactado profundamente pelo sistema de seguranca automobilistica. O sistema consiste em impedir acidentes ocasionados por uso de entorpecentes e males subitos. O circuito desse sistema consiste em: O piloto NAO deve estar sob efeito de entorpecente (!I), deve estar em boas condicoes fisicas e mentais (M) e o sistema NEURAL EVA deve estar atualizado (E). Contudo, se tiver um acompanhante habilitado (A) entao o acesso e permitido. Qual expressao representa corretamente esse sistema?",
    answer: "(!I & M & E) | (A)",
    difficulty: "Facil",
  },
  {
    name: "ROBOT EVA",
    question:
      "Durante uma competicao de lutas de robos, a equipe Iron Mind precisa usar a tatica STAIRWAY TO HEAVEN. As condicoes sao: O sensor de obstaculo deve identificar o inimigo (S), o robo deve estar com mais de 50% de bateria (B), e o robo inimigo deve estar a 1 metro de distancia (D). Essas verificacoes so sao realizadas caso o operador pressione o botao de ativacao (H). Desenvolva o sistema logico.",
    answer: "(S & B & D) & H",
    difficulty: "Facil",
  },
  {
    name: "Next Eva",
    question:
      "Um sistema de resfriamento inteligente para servidores so e acionado automaticamente se: A temperatura ambiente ultrapassar 30 graus (T), a taxa de uso da CPU ultrapassar 80% (C), e o sensor de movimento detectar que nao ha tecnicos no local (M). Essas condicoes so sao verificadas se o botao de seguranca for ativado (H). Desenvolva o circuito digital.",
    answer: "(T & C & M) & H",
    difficulty: "Facil",
  },
  {
    name: "Ciencia Vs Engenharia",
    question:
      "Para o desempate entre cursos, cada um deve montar um circuito logico que tem duas formas de checar se o usuario e cadastrado em um sistema de saque bancario: O usuario pode fazer a verificacao com a leitura da digital e do cartao, ou ele pode fazer o saque tendo a digital e a leitura de retina.",
    answer: "(D & C) | (D & R)",
    difficulty: "Facil",
  },
  {
    name: "Disjuntor logico",
    question:
      "Otavio, neste semestre, escolheu a eletiva de Eletrotecnica para ajudar sua mae a instalar um disjuntor em casa. Ele percebeu que o funcionamento do disjuntor se parece com logica digital. Faca o seu proprio circuito disjuntor, onde C e a corrente e T e o termico.",
    answer: "(C & T)",
    difficulty: "Facil",
  },
  {
    name: "Otavio Tech",
    question:
      "O protocolo de autenticacao da Otavio Tech e composto por: P: O usuario possui token valido; Q: O usuario esta em um IP confiavel. O sistema so libera o acesso se pelo menos uma das condicoes for verdadeira, e garantir que caso o token seja valido, o IP deve ser confiavel. Desenvolva esse circuito.",
    answer: "(P|Q)&(P>Q)",
    difficulty: "Facil",
  },
  {
    name: "Bracos Roboticos",
    question:
      "Um braco robotico so pode executar o encaixe da peca se ambos os sensores estiverem sincronizados: Um sensor de posicao mecanica (P) e um sensor de carga eletrica (Q). Qual e a expressao que representa esse sistema de montagem?",
    answer: "(P<>Q)",
    difficulty: "Facil",
  },
  {
    name: "Centauri Alpha",
    question:
      "O protocolo de autodestruicao da nave Centauri Alpha so pode ser iniciado se: A nave estiver fora da zona de seguranca (Z), o comandante inserir o codigo mestre (C), dois oficiais girarem suas chaves (K), e nenhum tripulante estiver presente (!M). O protocolo so pode ser checado se o sistema de comunicacao estiver offline (O). Monte a funcao booleana.",
    answer: "O&Z&C&K&!M",
    difficulty: "Facil",
  },
  {
    name: "Laboratorio Biocontido Nivel 5",
    question:
      "Para entrar no laboratorio e necessario ter cracha (C) e autorizacao biometrica (B). A entrada e liberada se e somente se o visitante tiver os dois requisitos ou nao tiver nenhum deles (modo de treinamento com seguranca desligada). Monte a funcao booleana.",
    answer: "B<>C",
    difficulty: "Facil",
  },
  {
    name: "Sistema de Triagem",
    question:
      "O sistema determina se um paciente deve ser transferido para a UDN. As condicoes sao: sinais neurologicos incomuns (N), historico genetico de doencas cerebrais (H), exame de bioimpedancia fora dos padroes (B). Se o paciente estiver com febre (F), e encaminhado para outra ala, a menos que o marcador imunologico (I) esteja abaixo do normal. Monte a funcao booleana.",
    answer: "(N & H & B)|(!F | I)",
    difficulty: "Medio",
  },
  {
    name: "Laboratorio de Genetica",
    question:
      "A contencao e ativada se: nivel de radiacao ultrapassa o limite (R), batimentos da celula genetica ultrapassam 250 (B), operador ativa emergencia (E). Se o sistema de backup genetico (G) estiver ativado e sensores de pressao (P) detectarem vazamento, a contencao e cancelada. Monte a funcao.",
    answer: "((R & B & E) & !(G & P))",
    difficulty: "Medio",
  },
  {
    name: "Controle de Drone de Resgate",
    question:
      "Um drone e liberado para voo autonomo quando: bateria acima de 40% (B), GPS na zona segura (Z), piloto habilitou modo autonomo (A). Se detectar tempestade (T), e proibido, a menos que carregue suprimentos medicos (M). Monte a funcao booleana.",
    answer: "(B&Z&A)&(!T|M)",
    difficulty: "Medio",
  },
  {
    name: "Lancamento de Foguete",
    question:
      "O lancamento e autorizado quando: sistemas criticos operacionais (C), combustivel acima do minimo (F), sem tempestade solar (!S). Se a base internacional estiver online (I), o sistema de comunicacao local (L) tambem deve estar ativo. Monte a funcao.",
    answer: "(C&F&!S)&(I>L)",
    difficulty: "Medio",
  },
  {
    name: "Cofre Bancario Inteligente",
    question:
      "O cofre so abre se: gerente inserir senha mestre (G) e sensor biometrico confirmar identidade (B). Se detectar invasao remota (R) ou gas de corte (X), se tranca automaticamente. Monte a funcao.",
    answer: "(G&B)&!(R|X)",
    difficulty: "Medio",
  },
  {
    name: "Estacao de Tratamento de Agua",
    question:
      "O sistema inicia a purificacao quando: nivel de agua bruta acima do minimo (N) e sensor de qualidade indica necessidade de tratamento (Q). Se a bomba principal estiver desligada (!P), o motor auxiliar (M) deve estar ligado. Monte a funcao.",
    answer: "(N&Q)&(!P>M)",
    difficulty: "Medio",
  },
  {
    name: "Aterrissagem Automatica",
    question:
      "O sistema de aterrissagem assistida e acionado quando: altitude abaixo de 500m (A), trem de pouso liberado (T), pista livre (P). Se houver vento lateral forte (V), e cancelada, exceto se o piloto ativar correcao automatica (C). Monte a expressao.",
    answer: "(A&T&P)&(!V|C)",
    difficulty: "Medio",
  },
  {
    name: "Seguranca de Submarino",
    question:
      "A sala de controle so pode ser acessada se: capitao autorizar (K) e scanner facial confirmar (F). Se o submarino estiver em modo de alerta (L), o scanner de retina (R) tambem deve validar. Qual a expressao?",
    answer: "(K&F)&(L>R)",
    difficulty: "Medio",
  },
  {
    name: "Robo Coletor Planetario",
    question:
      "O robo inicia a coleta quando: posicionado corretamente (P) e broca em funcionamento (B). Se a temperatura for extrema (E), a coleta so continua se o modulo de resfriamento estiver ligado (M). Quando o robo iniciara a coleta?",
    answer: "(P&B)&(!E|M)",
    difficulty: "Medio",
  },
  {
    name: "Satelite Espacial",
    question:
      "O satelite entra em modo de defesa se: detectar ameaca de colisao (C) e interferencia eletromagnetica (I). O sistema so e ativado se e somente se a antena de comunicacao estiver desligada (A = 0). Quando o satelite entrara em modo de defesa?",
    answer: "(C&I)&!A",
    difficulty: "Medio",
  },
  {
    name: "Irrigacao Inteligente",
    question:
      "O sistema libera agua quando: sensor de umidade indica nivel baixo (U) e sensor meteorologico preve ausencia de chuva (R). Se o tanque estiver abaixo de 20% (T), a irrigacao e bloqueada, a menos que a estufa esteja no modo de emergencia (E).",
    answer: "(U&R)&(!T|E)",
    difficulty: "Medio",
  },
  {
    name: "Rede Neural de Defesa de Orion",
    question:
      "As torres de plasma so disparam se: radar detectar naves nao registradas (R), campo gravitacional indicar aproximacao rapida (G), protocolo de combate autorizado (C). Se o campo de camuflagem (K) estiver ativo, o disparo e suspenso, a menos que esteja prestes a falhar (F). Se o comandante supremo estiver presente (S), o protocolo so e valido se a verificacao biometrica (B) estiver ativa.",
    answer: "(R&G&C&(!K|F))&(S>B)",
    difficulty: "Dificil",
  },
  {
    name: "Cofre Temporal de Kairos",
    question:
      "O cofre temporal so abre quando: relogio quantico aponta alinhamento correto (A), professor insere codigo mestre (M), campo de isolamento temporal esta estavel (E). Se o detector de paradoxos (P) estiver ativo, a abertura e bloqueada, a menos que o cristal esteja em modo de contencao quantica (Q). Se um assistente (L) estiver presente, deve ter passado pelo scanner de integridade quantica (I).",
    answer: "(A&M&E&(!P|Q))&(L>I)",
    difficulty: "Dificil",
  },
  {
    name: "Ponte Aerea de Nova Alexandria",
    question:
      "O sistema libera um drone para voo se: pista de decolagem livre (D), modulo de navegacao calibrado (N), combustivel acima de 60% (F). Se bloqueio aereo militar (B) estiver ativo, o voo so e autorizado se houver permissao de escolta (E) e o modulo de ocultacao termica (O) estiver ativo. Se a cidade estiver sob ataque terrestre (T), o voo so e liberado se o modo de evasao (V) estiver ativo.",
    answer: "(D&N&F&(!B|(E&O)))&(T>V)",
    difficulty: "Dificil",
  },
  {
    name: "Laboratorio Subterraneo de Borealis",
    question:
      "O reator criogenico e ativado se: temperatura do nucleo acima do limite (H), sistema de contencao magnetica ativo (M), operador confirmar ativacao manual (O). Se detectarem flutuacao gravitacional (G), o reator so liga se o modulo de compensacao (C) estiver ativo. Se o diretor de seguranca (S) estiver presente, o operador deve ter assinatura digital validada (V).",
    answer: "(H&M&O&(!G|C))&(S>V)",
    difficulty: "Dificil",
  },
  {
    name: "Cidade Submersa de Leviathan",
    question:
      "Os escudos sao ativados quando: sonar detecta formas se aproximando (X), campo de pressao ultrapassa o limite (P), reator online (R). Se detectarem atividade sismica (S), o sistema so e ativado se o modulo de reforco estrutural (E) estiver ligado. Se o prefeito (M) estiver a bordo, o protocolo diplomatico (D) deve estar desativado.",
    answer: "(X&P&R&(!S|E))&(M>!D)",
    difficulty: "Dificil",
  },
  {
    name: "Barreira de Venus Prime",
    question:
      "A barreira eletromagnetica e ativada quando: radar detecta plasma (P), rede de geradores acima de 80% (G), sistema de direcionamento calibrado (M). Se detectarem sobrecarga (S), a barreira so e ativada se o modulo de dissipacao (D) estiver funcionando. Se o governador (V) estiver presente, o protocolo de evacuacao (E) deve estar ativo.",
    answer: "(P&G&M&(!S|D))&(V>E)",
    difficulty: "Dificil",
  },
  {
    name: "Portal Interdimensional de Nyx",
    question:
      "A abertura do portal so ocorre se: tres geradores quanticos sincronizados (Q), fluxo de particulas estavel (F), codigo de autorizacao suprema inserido (A). Se o detector de instabilidade temporal (T) estiver ativo, a abertura e bloqueada a menos que o modulo de contencao temporal (C) esteja operando. Se um visitante diplomatico (D) estiver presente, o sistema de escudo dimensional (S) deve estar ativo.",
    answer: "(Q&F&A&(!T|C))&(D>S)",
    difficulty: "Dificil",
  },
  {
    name: "Trem Hipersonico de Chronos",
    question:
      "O sistema de aceleracao maxima e ativado se: pista limpa (L), motor em modo hipersonico (H), escudo aerodinamico em posicao (E). Se o clima for extremo (C), so e liberado se o sistema de estabilizacao (S) estiver ativo. Se o presidente da companhia (P) estiver a bordo, o modulo de seguranca VIP (V) deve estar ativado.",
    answer: "(L&H&E&(!C|S))&(P>V)",
    difficulty: "Dificil",
  },
  {
    name: "Fortaleza Orbital de Helios Prime",
    question:
      "O Canhao Solar Omega so dispara se: sensor optico detectar multiplos alvos (A), sistema de rastreamento confirmar propulsao ativa (H), reator de fusao em potencia maxima (R). Se o campo de camuflagem (C) estiver ativo, o disparo e proibido, a menos que o modulo de sobrecarga rapida (S) esteja ligado. Se um membro do Conselho Solar (M) estiver presente, o codigo de autorizacao dupla (D) deve ser validado. Se os sensores gravitacionais detectarem instabilidade (G), o disparo so e permitido se e somente se o estabilizador de trajetoria (T) estiver ligado.",
    answer: "(A&H&R&(!C|S)&((G>T)&(T>G))&(M>D))",
    difficulty: "Dificil",
  },
  {
    name: "Superlaser da Estrela da Morte",
    question:
      "O disparo do superlaser so e autorizado se: alvo travado e confirmado (A), reator de hiermateria em potencia maxima (R), convergencia dos oito feixes alinhada (C). Se o sistema de contencao de energia detectar instabilidade (I), o disparo e abortado, a menos que os canais de energia secundarios sejam redirecionados (S). Se o Imperador Palpatine estiver supervisionando (P), o codigo de anulacao de seguranca Omega (O) deve ser inserido. Se a frota imperial estiver na zona de fogo (F), o disparo so e permitido se e somente se o escudo defletor (E) estiver sincronizado.",
    answer: "(A&R&C&(!I|S))&(P>O)&(E<>F)",
    difficulty: "Dificil",
  },
  {
    name: "Projeto Belcan: A Senciencia Final",
    question:
      "A Senciencia e alcancada se: Rede Neural atingir sinapses trilionarias ativas (N), Base de Dados Universal assimilada (D), Framework Etico compilado sem paradoxos (E). Protocolo de Anomalia Quantica: Se detectar paradoxo quantico (Q), a ignicao e bloqueada, a menos que o modulo de resolucao (R) esteja ativo. Protocolo de Supervisao Humana: Se o Professor (P) iniciar o comando, sua assinatura biometrica (B) deve ser validada. Protocolo do Interruptor de Schrodinger: a ignicao so prossegue se o campo de contencao externo (C) estiver ativo se e somente se o interruptor interno (K) estiver desativado. Paradoxo da Criatividade: o Teste de Turing Invertido (T) so e bem-sucedido se criatividade genuina (G) ou consciencia emocional (S), mas nao ambos.",
    answer: "((N&D&E)&(!Q|R)&(P>B)&(!(C<>K))&(T>(!(G<>S))))",
    difficulty: "Supremo",
  },
]

export function getProblemsByDifficulty(difficulty: string): Problem[] {
  return PROBLEMS_BANK.filter((p) => p.difficulty === difficulty)
}

export function getDifficultyColor(difficulty: string): string {
  switch (difficulty) {
    case "Facil":
      return "text-success"
    case "Medio":
      return "text-warning"
    case "Dificil":
      return "text-destructive"
    case "Supremo":
      return "text-[#72076E]"
    default:
      return "text-muted-foreground"
  }
}

export function getDifficultyBadgeClass(difficulty: string): string {
  switch (difficulty) {
    case "Facil":
      return "bg-success/20 text-success border-success/30"
    case "Medio":
      return "bg-warning/20 text-warning border-warning/30"
    case "Dificil":
      return "bg-destructive/20 text-destructive border-destructive/30"
    case "Supremo":
      return "bg-[#72076E]/20 text-[#72076E] border-[#72076E]/30"
    default:
      return "bg-muted text-muted-foreground border-border"
  }
}
