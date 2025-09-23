import customtkinter as ctk

class Problems:
    def __init__(self, name, question, answer, difficulty ):
        self.name = name 
        self.question = question 
        self.answer = answer
        self.difficulty = difficulty 

    def show_the_problem(self):
        # print(f"{self.name}")
        # print(f"{self.question} \nLevel : {self.difficulty}")
        pass

    def show_the_answer(self):
        print(f"The boolean answer is : {self.answer}")

class ProblemsToFrame:
    def __init__(self, problem_bank):
        self.problems = problem_bank
    
    def get_frame_from_number(self, index):
        return Problems_bank[index]

    def create_frame_from_problem(self, question_number, window):
        current_problem = self.get_frame_from_number(question_number)
        frame = ctk.CTkFrame(window, fg_color="#082347")
        frame.grid(row=0, column=0, sticky="nsew")

        label_name = ctk.CTkLabel(frame, text=current_problem.name, font=("Trebuchet MS", 20), text_color="white")
        label_name.pack(pady=10)

        label_question = ctk.CTkLabel(frame, text=current_problem.question, font=("Trebuchet MS", 14), text_color="white")
        label_question.pack(pady=10)

        label_answer = ctk.CTkLabel(frame, text=f"Answer: {current_problem.answer}", font=("Trebuchet MS", 14), text_color="white")
        label_answer.pack(pady=10)

        botao_voltar = ctk.CTkButton(frame, text="Voltar", command=lambda: self.show_problems_frame(window))
        botao_voltar.pack(pady=20)

        return frame

Problems_bank = [
    Problems(
        name = "Airbags",
        question = """
        Larissa é uma engenheira(o) de software muito dedicada(o). 
        Em um de seus trabalhos na empresa automobilística, Evandro's,
        lhe foi confiada(o) o desenvolvimento de um circuito lógico para
        o sistema de airbags dos carros da empresa. Devido ao prazo curto
        de entrega Larissa pede sua ajuda para o desenvolvimento do circuito,
        que só deve ser ativado sob as seguintes condições :
        O veículo deve estar em movimento (V),o passageiro deve estar no carro (P)
        e o sensor de impacto deve estar ativado (I).
        """,
        answer = "(V & P & I)",
        difficulty = "Fácil"
    ),
    Problems(
        name = "Sem mais acidentes",
        question = """
        Nos anos 3000 o sistema de transporte mundial foi impactado profundamente pelo 
        sistema de segurança automobilística desenvolvido pelo doutor em engenharia de 
        computação,  Dr. Zilderlan. O sistema consistia em impedir acidentes ocasionados 
        por uso de entorpecentes e males súbitos, redirecionando o condutor ao banco de 
        passageiros, impedindo ele acessar o volante do veículo, permitindo assim que o
        automóvel inteligente fizesse todo o trabalho. O circuito desse sistema revolucionário 
        consistia em algumas leis : O piloto NÃO deve estar sob o efeito de nenhum 
        entorpecente(-I), ele deve estar em boas condições físicas e mentais (M) e  o 
        sistema NEURAL EVA deve estar atualizado (E). Contudo, se tiver um 
        acompanhante habilitado (A) então o banco da frente pode ser acessado. 
        """,
    answer = "(!I & M & E) | (A)",
    difficulty = "Fácil"
    ),
    Problems(
        name = "ROBOT EVA",
        question = """
        Durante o maior evento de competição de lutas de robôs, ROBOT EVA, a equipe 
        Iron Mind lidera as seletivas de finais, mas um problema surgiu. A equipe rival,
        Asimov, desenvolveu uma estratégia infalível que batia de frente com a Iron Mind. A 
        equipe não teve escolha a não ser usar a sua tática infalível, nunca mostrada em 
        nenhuma competição, a STAIRWAY TO HEAVEN. Essa tática de combate é 
        condicional e é ativada separadamente por um circuito especial presente no robô. As 
        condições são : 
        - O sensor de obstáculo deve identificar o inimigo (S)
        - O robô deve estar mais de 50 % de bateria (B)
        - E o robô inimigo deve estar a 1 metro de distância (D)
        No entanto, por ser um ataque de alta precisão e que consome muita energia, essas 
        verificações só são realizadas caso o operador pressione o botão de ativação (H). Ou 
        seja, o sistema só será liberado se o botão for pressionado e todas as condições forem 
        verdadeiras.
        Ajude a equipe Iron Mind a desenvolver esse sistema lógico antes do próximo round!
        """,
    answer = "(S & B & D) & H",
    difficulty = "Fácil"
    ),
    Problems(
        name = "Next Eva",
        question = """
        Durante a manutenção de servidores na sede da empresa de tecnologia Nex Eva,
        um novo sistema de resfriamento inteligente foi implementado para evitar o 
        superaquecimento das máquinas durante os picos de uso.

        O sistema de resfriamento só é acionado automaticamente se três condições
        forem atendidas:

            - A temperatura ambiente ultrapassar os 30 °C (T);
            - A taxa de uso da CPU ultrapassar 80% (C);
            - E o sensor de movimento detectar que não há técnicos no local (M).

        Para evitar acionamentos desnecessários durante inspeções manuais, essas 
        condições só são verificadas se o botão de segurança for ativado (H), 
        geralmente ao final de cada turno.

        Ajude a equipe da Nex Eva a desenvolver o circuito digital que representa esse sistema.
        """,
    answer = "(T & C & M) & H",
    difficulty = "Fácil"
    ),
    Problems (
        name = "Ciência Vs Engenharia",
        question = """
        Os alunos de engenharia de computação e  ciência da computação do IC se 
        encontram em um embate milenar. Para o desempate, cada curso deve montar um 
        circuito lógico que tem duas formas de checar a se o usuário é cadastrado em um 
        sistema de saque bancário : 
            - O usuário pode fazer a verificação com a leitura da digital e do cartão
            - Ou ele pode fazer o saque tendo a digital e a leitura de retina 
        Ajude a turma de engenharia a ganhar esse empate.
        """,
    answer = "(D & C) | (D & R)",
    difficulty = "Fácil"
    ),
    Problems(
        name = "Disjuntor lógico",
        question = """
        Otávio, neste semestre, escolheu a eletiva de Eletrotécnica com o objetivo de 
        ajudar sua mãe a instalar um disjuntor em casa. Durante as aulas, ele percebeu 
        que o funcionamento do disjuntor se parecia muito com um conceito que havia 
        aprendido na disciplina de Lógica e Circuitos Digitais. Com essa ideia em mente, 
        Otávio resolveu desenvolver um circuito lógico que simulasse o comportamento do 
        disjuntor, utilizando os conhecimentos adquiridos nas duas matérias. Agora faça o
        seu próprio circuito disjuntor.

        """,
    answer = "(C & T)",
    difficulty = "Fácil"
    ),
    Problems(
        name = "Otávio Tech",
        question = """
        Durante o desenvolvimento de um sistema avançado de controle de acesso 
        distribuído, a equipe de segurança da empresa Otávio Tech criou um protocolo 
        lógico de autenticação para evitar acessos indevidos a servidores críticos.

        Esse protocolo é composto por duas condições principais que determinam se um 
        acesso deve ser concedido (S = 1) ou negado (S = 0):

            - P: O usuário possui token de autenticação válido;
            - Q: O usuário está acessando a partir de um IP confiável.

        O sistema só libera o acesso se pelo menos uma dessas condições for 
        verdadeira (ou seja, P | Q) e, ao mesmo tempo, garantir que caso o token seja 
        válido (P = 1), então obrigatoriamente o IP deve ser confiável (Q = 1). Isso evita 
        que usuários com token roubado acessem de redes inseguras. Ajude a equipe da Otávio 
        Tech a desenvolver esse circuito.

        """,
    answer = "(P|Q)&(P>Q)",
    difficulty = "Fácil"
    ),
    Problems(
        name = "Braços Robóticos",
        question = """
        Durante o desenvolvimento de um braço robótico automatizado para a linha de 
        montagem da empresa TechLine Robotics, foi necessário implementar um sistema 
        de segurança que garante a sincronização entre dois sensores essenciais:

            - Um sensor de posição mecânica (P) que detecta se o braço está no ponto 
            exato de encaixe da peça;
            - Um sensor de carga elétrica (Q) que verifica se o motor está com a voltagem 
            correta para realizar o encaixe com segurança.

        Por questões de segurança, o robô só poderá executar o encaixe da peça se 
        ambos os sensores estiverem sincronizados, ou seja, os dois ativos ao mesmo 
        tempo, ou os dois inativos ao mesmo tempo.
        """,
    answer = "!(P>Q)&(Q>P)",
    difficulty = "Fácil"
    ),
    Problems(
        name = "Centauri Alpha",
        question = """
        Durante uma expedição intergaláctica em 2129, a nave Centauri Alpha sofre um 
        ataque alienígena inesperado. Como última medida de contenção, o comandante 
        ativou o protocolo de autodestruição da nave, que só pode ser iniciado se todas as 
        condições abaixo forem satisfeitas:

            - A nave estiver fora da zona de segurança orbital (Z).
            - O comandante inserir o código mestre corretamente (C).
            - Dois oficiais de segurança girarem simultaneamente suas chaves de ativação (K).
            - Nenhum tripulante estiver presente nos módulos centrais da nave (-M).

        Além disso, por segurança, o protocolo só pode ser checado se o sistema de
        comunicação estiver completamente offline (O), impedindo transmissões externas.
        Monte a função booleana que representa o sistema de autodestruição

        Dica: Todos os termos são necessários e o protocolo só é ativado se o sistema 
        estiver offline.
        """,
    answer = "O&Z&C&K&!M",
    difficulty = "Fácil"
    ),
    Problems(
        name = "Sistema de Triagem",
        question = """
        No hospital mais avançado da América Latina, um novo sistema de triagem médica
        foi instalado. Ele determina se um paciente deve ser imediatamente transferido para
        a Unidade de Diagnóstico Neural (UDN).

        As condições são:

            - O paciente apresenta sinais neurológicos incomuns (N).
            - Há histórico genético de doenças cerebrais na família (H).
            - O exame de bioimpedância neural retornou fora dos padrões (B).

        No entanto, se o paciente estiver com febre (F), ele deve ser encaminhado para 
        outra ala primeiro, a menos que o valor do marcador imunológico (I) esteja 
        abaixo do normal (nesse caso, a febre é considerada efeito secundário, e o paciente 
        pode ir para a UDN mesmo com febre).
        Monte a função booleana que representa o envio para a UDN.
        """,
    answer = "(N & H & B)|(!F | I)",
    difficulty = "Média"
    ),
    Problems(
        name = "Laboratório de Genética",
        question = """
        Em um laboratório de pesquisas genéticas de alto risco, um sistema de contenção 
        foi desenvolvido para impedir que organismos modificados escapem para o 
        ambiente externo. A contenção é ativada se:

            - O nível de radiação ultrapassa o limite de segurança (R).
            - O número de batimentos da célula genética por segundo ultrapassa 250 (B).
            - O operador ativa o botão de emergência (E).

        Entretanto, se o sistema de backup genético (G) estiver ativado e os sensores de 
        pressão (P) detectarem vazamento de gás, a contenção deve ser cancelada 
        (mesmo que as outras condições estejam satisfeitas), pois isso indica que a 
        contenção pode causar colapso do organismo e gerar mutações indesejadas.

        Monte a função que define o acionamento da contenção.
        """,
    answer = "((R & B & E) & !(G & P))",
    difficulty = "Média"
    ),
    Problems(
        name = "Controle de Drone de Resgate",
        question = """
        Durante missões de resgate em áreas de difícil acesso, um drone
        especial é liberado para voar em modo autônomo apenas quando:

            - O nível de bateria é superior a 40% (B).
            - O GPS indica que está na zona de operação segura (Z).
            - O piloto habilitou o modo autônomo (A).

        No entanto, se o sensor climático detectar tempestade (T), o voo autônomo é 
        proibido, a menos que o drone esteja carregando suprimentos médicos de 
        emergência (M), caso em que a missão é prioridade.

        Monte a função booleana que representa esse sistema.
        """,
    answer = "(B&Z&A)&(!T|M)",
    difficulty = "Média"
    ),
    Problems(
        name = "Sistema de Autorização de Lançamento de Foguete",
        question = """
        No centro espacial internacional, o lançamento só é autorizado quando:

            - Todos os sistemas críticos estão operacionais (C).
            - O combustível está acima do nível mínimo (F).
            - Não há tempestade solar (S).

        Além disso, o protocolo exige que se a base de controle internacional estiver 
        online (I), então o sistema de comunicação local (L) também deve estar ativo.

        Monte a função booleana que represente as condições de lançamento.
        """,
    answer = "(C&F&!S)&(I>L)",
    difficulty = "Média"
    ),
    Problems(
        name = "Sistema de Bloqueio de Cofre Bancário Inteligente",
        question = """
        Um cofre bancário de alta segurança só abre se:

            - O gerente presente no local inserir a senha mestre (G).
            - O sensor biométrico confirmar a identidade (B).

        No entanto, se o sistema detectar tentativa de invasão remota (R) ou gás de corte de
        metal (X), o cofre se tranca automaticamente, independentemente das outras 
        condições.
        Monte a função booleana que represente a abertura do cofre.
        """,
    answer = "(G&B)&!(R|X)",
    difficulty = "Média"
    ),
    Problems(
        name = "Sistema de Entrada em Laboratório Biocontido Nível 5",
        question="""
        Para entrar no laboratório:

            - É necessário possuir crachá de acesso especial (C).
            - Ter autorização biométrica (B).

        O sistema possui ainda uma verificação lógica:

            - A entrada é liberada se e somente se o visitante tiver os dois requisitos
            (crachá e biometria) ou não tiver nenhum deles (modo de treinamento com 
            segurança total desligada).

        Monte a função booleana que represente o sistema.
        """,
        answer = "(C>B)&(B>C)",
        difficulty = "Fácil"
    ),
    Problems(
        name = "Sistema de Controle de Estação de Tratamento de Água",
        question = """
        O sistema inicia o processo de purificação quando:

            - O nível de água bruta está acima do mínimo (N).
            - O sensor de qualidade indica necessidade de tratamento (Q).

        Por segurança, se a bomba principal estiver desligada (P = 0), então o motor 
        auxiliar (M) deve estar ligado para iniciar o processo.

        Monte a função booleana do sistema.
        """,
        answer = "(N&Q)&(!P>M)",
        difficulty = "Média"
    ),
    Problems(
        name = "Sistema de Aterrissagem Automática de Aviões",
        question= """
        Um sistema de aterrissagem assistida é acionado quando:

            - O avião está abaixo de 500 metros de altitude (A).
            - O trem de pouso está liberado (T).
            - A pista está livre (P).

        Se houver vento lateral forte (V), a aterrissagem assistida é cancelada, exceto se o 
        piloto ativar o modo de correção automática (C).
        """,
        answer= "(A&T&P)&(!V|C)",
        difficulty= "Média"
    ),
    Problems(
        name = " Sistema de Segurança de Submarino",
        question = """

        A sala de controle de um submarino só pode ser acessada se:

            - O capitão autorizar a entrada (K).
            - O scanner facial confirmar a identidade (F).

        Além disso, se o submarino estiver em modo de alerta (L), então o scanner de 
        retina (R) também deve validar.
        """,
        answer = "(K&F)&(L>R)",
        difficulty = "Média"
    ),
    Problems(
        name = "Robô Coletor de Amostras Planetárias",
        question = """
        O robô inicia a coleta quando:

            - Está posicionado corretamente sobre a amostra (P).
            - A broca está em funcionamento (B).

        Se a temperatura ambiente for extrema (E), a coleta só continua se o módulo de 
        resfriamento estiver ligado (M).
        """,
        answer = "(P&B)&(!E|M)",
        difficulty = "Média"
    ),
    Problems(
        name = "Sistema de Autoproteção de Satélite Espacial",
        question = """
        O satélite entra em modo de defesa se:

            - Detectar ameaça de colisão (C).
            - Detectar interferência eletromagnética (I).

        Além disso, o sistema só é ativado se e somente se a antena de comunicação 
        estiver desligada (A = 0).
        """,
        answer = "(C&I)&!A",
        difficulty = "Média"
    ),
    Problems(
        name = "Controle de Irrigação Inteligente",
        question = """
        Um sistema agrícola libera água quando:

            - O sensor de umidade do solo indica nível baixo (U).
            - O sensor meteorológico prevê ausência de chuva (R).

        No entanto, se o tanque de água estiver abaixo de 20% (T), a irrigação é 
        bloqueada, a menos que a estufa esteja no modo de emergência (E).

        """,
        answer = "(U&R)&(!T|E)",
        difficulty = "Média"
    ),
    Problems(
        name = "A Rede Neural de Defesa de Orion",
        question = """
        Ano 2197. A colônia espacial Orion está sob ameaça de uma frota 
        pirata interplanetária. O conselho de segurança instalou um sistema de defesa 
        automatizado, a Rede Neural Aegis, que só dispara suas torres de plasma se:

            - O radar detectar naves não registradas (R).
            - O campo gravitacional indicar aproximação rápida (G).
            - O protocolo de combate estiver autorizado pelo conselho (C).

        Contudo, se o campo de camuflagem da colônia estiver ativo (K), o disparo é 
        suspenso para evitar revelar a posição — a menos que o campo de camuflagem 
        esteja prestes a falhar (F), caso em que o disparo é imediato.

        Além disso, se o comandante supremo estiver presente (S), então o protocolo 
        de combate (C) só é válido se o sistema de verificação biométrica do 
        comandante estiver ativo (B).
        """,
        answer = "(R&G&C&(!K|F))&(S>B)",
        difficulty = "Difícil"
    ),
    Problems(
        name = "O Cofre Temporal da Universidade de Kairós",
        question = """
        No laboratório de física quântica, um cofre temporal guarda um cristal 
        capaz de alterar linhas do tempo. Ele só abre quando:

            - O relógio quântico aponta o alinhamento correto (A).
            - O professor-chefe insere o código mestra (M).
            - O campo de isolamento temporal está estável (E).

        Por segurança, se o detector de paradoxos (P) estiver ativo, a abertura é 
        bloqueada — a menos que o cristal já esteja em modo de contenção quântica (Q).

        Além disso, se um assistente de laboratório estiver presente (L), então é 
        obrigatório que ele tenha passado pelo scanner de integridade quântica (I).

        """,
        answer = "(A&M&E&(!P|Q))&(L>I)",
        difficulty = "Difícil"
    ),
    Problems(
        name = "A Ponte Aérea de Nova Alexandria",
        question = """
        Durante uma evacuação emergencial, drones cargueiros transportam
        civis pela ponte aérea.
        O sistema libera um drone para voo apenas se:

            - A pista de decolagem estiver livre (D).
            - O módulo de navegação estiver calibrado (N).
            - O nível de combustível estiver acima de 60% (F).

        Mas, se um bloqueio aéreo militar (B) estiver ativo, o voo só é autorizado se
        houver permissão de escolta da frota de defesa (E) e o módulo de ocultação térmica
        estiver ativo (O).

        Além disso, se a cidade estiver sob ataque terrestre (T), então o voo só é 
        liberado se o modo de evasão estiver ativo (V).
        """,
        answer = "(D&N&F&(!B|(E&O)))&(T>V)",
        difficulty = "Difícil"
    ),
    Problems(
        name = "O Laboratório Subterrâneo de Borealis",
        question = """
        No subsolo da geleira Borealis, cientistas estudam partículas exóticas instáveis.
        O reator criogênico é ativado apenas se:

            - A temperatura do núcleo estiver acima do limite seguro (H).
            - O sistema de contenção magnética estiver ativo (M).
            - O operador principal confirmar ativação manual (O).

        Se os sensores detectarem flutuação gravitacional (G), o reator só liga se o 
        módulo de compensação estiver ativo (C).

        Por protocolo, se o diretor de segurança estiver presente (S), então o operador 
        principal (O) deve ter sua assinatura digital validada (V).
        """,
        answer = "(H&M&O&(!G|C))&(S>V)",
        difficulty = "Difícil"
    ),
    Problems(
        name = "A Cidade Submersa de Leviathan",
        question = """
        A cidade submersa Leviathan depende de um sistema de escudos 
        energéticos contra monstros abissais.
        Os escudos são ativados quando:

            - O sonar detecta grandes formas se aproximando (X).
            - O campo de pressão externa ultrapassa o limite (P).
            - O reator de energia está online (R).

        Se os sensores detectarem atividade sísmica (S), o sistema de escudos só é 
        ativado se o módulo de reforço estrutural estiver ligado (E).

        Por protocolo, se o prefeito estiver a bordo (M), então o sistema de escudos só é 
        acionado se o protocolo diplomático com criaturas inteligentes (D) estiver 
        desativado.
        """,
        answer = "X&P&R&(!S|E))&(M>!D)",
        difficulty = "Difícil"
    ),
        Problems(
        name = "A Barreira de Contenção de Vênus Prime",
        question = """
        No planeta-colônia Vênus Prime, uma barreira eletromagnética protege
        as cidades flutuantes contra tempestades de plasma.
        A barreira é ativada quando:

            - O radar climático detecta plasma em aproximação (P).
            - A rede de geradores está operando acima de 80% (G).
            - O sistema de direcionamento magnético está calibrado (M).

        No entanto, se os sensores detectarem sobrecarga elétrica (S), a barreira só é 
        ativada se o módulo de dissipação estiver funcionando (D).

        Além disso, se o governador estiver presente (V), então o protocolo de 
        evacuação de emergência (E) deve estar ativo antes da barreira ser acionada.
        """,
        answer = "(P&G&M&(!S|D))&(V>E)",
        difficulty = "Difícil"
    ),
        Problems(
        name = "O Portal Interdimensional de Nyx",
        question = """
        Nos confins da galáxia, a estação científica Nyx abriga um portal 
        interdimensional.
        A abertura do portal só ocorre se:

            - Os três geradores quânticos estiverem sincronizados (Q).
            - O fluxo de partículas estiver estável (F).
            - O código de autorização suprema for inserido (A).

        Se o detector de instabilidade temporal (T) estiver ativo, a abertura é bloqueada 
        a menos que o módulo de contenção temporal (C) esteja operando.

        Por segurança, se um visitante diplomático estiver presente (D), então o sistema
        de escudo dimensional (S) deve estar ativo antes da abertura.
        """,
        answer = "(Q&F&A&(!T|C))&(D>S)",
        difficulty = "Difícil"
    ),
        Problems(
        name = "O Trem Hipersônico de Chronos",
        question = """
        O Chronos-9 é um trem hipersônico que atravessa continentes em minutos.
        O sistema de aceleração máxima é ativado apenas se:

            - A pista estiver totalmente limpa (L).
            - O motor estiver no modo hipersônico (H).
            - O escudo aerodinâmico estiver em posição (E).

        Se o clima for extremo (C), a aceleração máxima só é liberada se o sistema de
        estabilização estiver ativo (S).

        Por protocolo, se o presidente da companhia estiver a bordo (P), então o módulo 
        de segurança VIP (V) deve estar ativado.
        """,
        answer = "(L&H&E&(!C|S))&(P>V)",
        difficulty = "Difícil"
    ),
        Problems(
        name = "A Fortaleza Orbital de Helios Prime",
        question = """
        Ano 2334. A Fortaleza Helios Prime é a última defesa da Terra contra 
        enxames de naves dronadas inimigas.
        O Canhão Solar Omega só dispara se:

            - O sensor óptico detectar múltiplos alvos (A).
            - O sistema de rastreamento de calor confirmar propulsão ativa nas naves (H).
            - O reator de fusão estiver em potência máxima (R).

        Além disso, existe um protocolo de segurança triplo:

            1. Se o campo de camuflagem da fortaleza estiver ativo (C), o disparo é 
            proibido, a menos que o módulo de sobrecarga rápida esteja ligado (S).
            2. Se um membro do Conselho Solar estiver presente (M), então o disparo
            só é autorizado se o código de autorização dupla (D) for validado.
            3. Se os sensores gravitacionais detectarem instabilidade (G), o disparo só 
            é permitido se e somente se o estabilizador de trajetória estiver ligado (T).

            Desafio: monte a função booleana e um circuito que representa todo o sistema.
        """,
        answer = "(A&H&R&(!C|S)&((G>T)&(T>G))&(M>D)",
        difficulty = "Difícil"
    ),

]
print(f"{Problems_bank[0].show_the_problem()}")