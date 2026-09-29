from datetime import date

class Pessoa:
    """
    Classe base que concentra os dados de identificação comuns a qualquer 
    pessoa na instituição (nome, CPF, telefone e e-mail).
    """
    pass


class Aluno(Pessoa):
    """
    Especializa a classe Pessoa, adicionando uma matrícula única e um histórico 
    acadêmico. Responsável também por calcular o Coeficiente de Rendimento (CR).
    """
    def calcular_cr(self) -> float:
        """Calcula o coeficiente de rendimento/média ponderada com base nas disciplinas do histórico."""
        pass


class Curso:
    """
    Representa a disciplina na sua essência. Guarda a ementa, carga horária 
    e a lista de pré-requisitos necessários para ser cursada.
    """
    def verificar_ciclo_dependencia(self, novo_pre_requisito: str) -> bool:
        """Impede dependências cruzadas (ex: A exige B e B exige A simultaneamente)."""
        pass


class Oferta:
    """
    Classe base que abstrai o conceito de algo sendo oferecido no tempo e espaço, 
    contendo o período letivo, horários, local e limite de vagas.
    """
    pass


class Turma(Oferta):
    """
    Herda de Oferta e concretiza a oferta de um Curso específico em um semestre. 
    Controla o próprio status (aberta/fechada) e possui a lógica contra choques de horário.
    """
    def abrir_turma(self) -> None:
        """Altera o status da turma para 'Aberta'."""
        pass

    def fechar_turma(self) -> None:
        """Altera o status da turma para 'Fechada', impedindo novas matrículas."""
        pass

    def verificar_choque_horario(self, outra_turma) -> bool:
        """Verifica se os horários desta turma conflitam com os de uma turma já matriculada."""
        pass


class Matricula:
    """
    Classe associativa que conecta um Aluno a uma Turma. Guarda as notas, a frequência 
    e atualiza o status de aprovação com base nas regras do sistema.
    """
    def lancar_nota(self, nota: float) -> None:
        """Adiciona uma nova nota validada à lista de notas do aluno nesta turma."""
        pass

    def lancar_frequencia(self, frequencia: float) -> None:
        """Atualiza a porcentagem de frequência do aluno."""
        pass

    def atualizar_situacao(self, regras) -> None:
        """Calcula a situação final do aluno com base nas notas, frequência e regras vigentes."""
        pass

    def trancar_matricula(self, data_atual: date, data_limite: date) -> bool:
        """Valida e processa a desistência da disciplina dentro do prazo estipulado."""
        pass


class Configuracao:
    """
    Responsável por isolar as regras de negócio parametrizáveis. Lê dados de 
    um arquivo (JSON) e centraliza parâmetros como notas mínimas e prazos de trancamento.
    """
    def carregar_configuracoes(self) -> None:
        """Lê os dados do arquivo JSON de configuração e atualiza os atributos da classe."""
        pass

    def get_instancia(self):
        """Retorna a instância única de configuração."""
        pass


class Sistema:
    """
    Classe principal de controle. Garante o funcionamento da CLI, armazenando 
    as listas em memória, coordenando cadastros, efetivando matrículas e gerando relatórios.
    """
    def cadastrar_curso(self, curso: Curso) -> None:
        """Adiciona um novo curso ao catálogo disponível do sistema."""
        pass

    def cadastrar_aluno(self, aluno: Aluno) -> None:
        """Adiciona um novo aluno à lista geral de alunos matriculados na instituição."""
        pass

    def abrir_turma(self, turma: Turma) -> None:
        """Adiciona uma nova oferta de turma à lista de turmas ativas."""
        pass

    def realizar_matricula(self, matricula_aluno: str, id_turma: str) -> None:
        """Localiza as instâncias e realiza as validações (choque, vagas, pré-requisitos) para criar uma Matrícula."""
        pass

    def salvar_estado(self) -> None:
        """Escreve os dados das listas em memória para um arquivo JSON."""
        pass

    def carregar_estado(self) -> None:
        """Carrega os dados lidos em disco para as listas na memória do sistema."""
        pass

    # --- Métodos de Relatório ---
    
    def gerar_relatorio_alunos_turma(self, id_turma: str) -> None:
        """Mostra vagas ocupadas em relação às vagas totais de uma determinada turma."""
        pass

    def gerar_relatorio_taxa_aprovacao(self) -> None:
        """Mostra a quantidade de aprovações nas turmas em relação à quantidade de matriculados."""
        pass

    def gerar_relatorio_distribuicao_notas(self, id_turma: str) -> None:
        """Calcula média, mediana e desvio padrão das notas de uma turma específica."""
        pass

    def gerar_relatorio_alunos_risco(self) -> None:
        """Lista os alunos com nota ou frequência abaixo dos parâmetros definidos nas configurações."""
        pass

    def gerar_relatorio_top_n(self, periodo: str) -> None:
        """Usa o atributo top_n_alunos da configuração para ordenar os CRs e retornar os melhores alunos."""
        pass
