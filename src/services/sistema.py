from src.domain.models.alunos import Aluno
from src.domain.models.turmas import Turma
from src.domain.models.cursos import Curso
from src.domain.models.matriculas import Matricula
from src.domain.models.graduacoes import Graduacao
from src.config.config import Configuracao


# Construção da classe.
class Sistema:
    """
    Classe principal de controle. Garante o funcionamento da CLI, armazenando as listas
    (graduações, cursos, turmas, alunos) em memória, coordenando cadastros e matrículas.
    """


    def __init__(self, configuracao: Configuracao) -> None:

        # Atribui e valida a instância de configuração contendo as regras de negócio.
        self.configuracao = configuracao

        # Inicializa as coleções em memória como listas vazias no momento da criação.
        self._alunos = []

        self._turmas = []

        self._cursos = []

        self._graduacoes = []


    @property
    def configuracao(self):
        return self._configuracao


    @configuracao.setter
    def configuracao(self, nova_configuracao: Configuracao):

        # Garante que apenas um objeto autêntico da classe Configuracao seja injetado.
        if not isinstance(nova_configuracao, Configuracao):
            raise TypeError("A configuração atribuída deve ser um objeto válido da classe 'Configuracao'!")

        self._configuracao = nova_configuracao


    # Propriedades de acesso às listas do sistema (sem setters para evitar sobrescrita acidental).
    @property
    def alunos(self):
        return self._alunos


    @property
    def turmas(self):
        return self._turmas


    @property
    def cursos(self):
        return self._cursos


    @property
    def graduacoes(self):
        return self._graduacoes


    def cadastrar_aluno(self, nome: str, cpf: str, telefone: str, email: str, graduacao: Graduacao) -> Aluno:
        """Adiciona um novo aluno à lista geral de alunos matriculados na instituição e retorna a instância."""

        # Verifica se a graduação pretendida pelo aluno consta nos registros do sistema.
        if graduacao not in self._graduacoes:
            raise ValueError("A graduação informada para o aluno não está cadastrada no sistema!")

        # Instancia o aluno (acionando internamente as validações de Pessoa e Aluno).
        novo_aluno = Aluno(nome, cpf, telefone, email, graduacao)

        # Registra o novo aluno na coleção em memória do sistema.
        self._alunos.append(novo_aluno)

        return novo_aluno


    def cadastrar_graduacao(self, codigo_mec: str, nome: str, qtd_semestres: int) -> Graduacao:
        """Adiciona um novo curso superior à lista de graduações ofertadas pela instituição e retorna a instância."""

        # Instancia a nova graduação validando código MEC, nome e duração.
        nova_graduacao = Graduacao(codigo_mec, nome, qtd_semestres)

        # Registra a nova graduação na coleção em memória do sistema.
        self._graduacoes.append(nova_graduacao)

        return nova_graduacao


    def cadastrar_curso(self, nome: str, carga_horaria: int, pre_requisitos: list, ementa: str, graduacao: Graduacao) -> Curso:
        """Adiciona um novo curso (disciplina) ao catálogo disponível do sistema e retorna a instância."""

        # Impede o cadastro de disciplinas em graduações inexistentes no sistema.
        if graduacao not in self._graduacoes:
            raise ValueError(f"A graduação '{graduacao.nome}' não está cadastrada no sistema!")

        # Instancia o novo curso com suas regras de carga horária e pré-requisitos.
        novo_curso = Curso(nome, carga_horaria, pre_requisitos, ementa, graduacao)

        # Vincula a disciplina criada diretamente à grade curricular da graduação.
        graduacao.adicionar_disciplina(novo_curso)

        # Adiciona a disciplina ao catálogo geral de cursos do sistema.
        self._cursos.append(novo_curso)

        return novo_curso


    def abrir_turma(self, periodo: str, dias_horarios: dict, vagas: int, local: str, curso: Curso) -> Turma:
        """Adiciona uma nova oferta de turma à lista de turmas ativas e retorna a instância."""

        # Garante que o curso ofertado pertença ao catálogo oficial do sistema.
        if curso not in self._cursos:
            raise ValueError(f"O curso '{curso.nome}' não está cadastrado no catálogo do sistema!")

        # Instancia a turma (o construtor de Turma já a vincula automaticamente ao Curso).
        nova_turma = Turma(periodo, dias_horarios, vagas, local, curso)

        # Registra a nova oferta na lista geral de turmas do sistema.
        self._turmas.append(nova_turma)

        return nova_turma


    def realizar_matricula(self, aluno: Aluno, turma: Turma) -> Matricula:
        """Localiza as instâncias, realiza as validações e retorna o vínculo de Matrícula criado."""

        # Verifica se o aluno informado pertence aos registros ativos da instituição.
        if aluno not in self._alunos:
            raise ValueError(f"O aluno '{aluno.nome}' não está cadastrado no sistema!")

        # Verifica se a turma informada consta nas ofertas oficiais da instituição.
        if turma not in self._turmas:
            raise ValueError(f"A turma '{turma.id_turma}' não está cadastrada no sistema!")

        # Impede matrículas em turmas que já foram encerradas.
        if turma.status != "Aberta":
            raise ValueError(f"A matrícula não pode ser realizada pois a turma '{turma.id_turma}' está '{turma.status}'!")

        # Verifica a disponibilidade de vagas comparando matrículas ativas com o limite da oferta.
        if len(turma.matriculas_ativas) >= turma.vagas:
            raise ValueError(f"A turma '{turma.id_turma}' já atingiu o limite máximo de {turma.vagas} vagas!")

        # Filtra todas as turmas que o aluno já está cursando atualmente no semestre.
        disciplinas_ativas = {
            matricula.turma
            for matricula in aluno.historico
            if matricula.status == "Cursando"
        }

        # Filtra todos os cursos nos quais o aluno já obteve aprovação anteriormente.
        disciplinas_concluidas = {
            matricula.turma.curso
            for matricula in aluno.historico
            if matricula.status == "Aprovado"
        }

        # Impede que o aluno curse novamente uma disciplina em andamento ou já concluída.
        if turma in disciplinas_ativas or turma.curso in disciplinas_concluidas:
            raise ValueError(f"O aluno '{aluno.nome}' já está cursando ou já foi aprovado em '{turma.curso.nome}'!")

        # Verifica se o aluno atingiu o teto de disciplinas simultâneas permitido pela configuração.
        if len(disciplinas_ativas) >= self.configuracao.max_turmas_por_aluno:
            raise ValueError(
                f"O aluno '{aluno.nome}' já atingiu o limite máximo de "
                f"{self.configuracao.max_turmas_por_aluno} turmas simultâneas!"
            )

        # Verifica se algum pré-requisito exigido pela disciplina ainda não foi cumprido pelo aluno.
        for pre_requisito in turma.curso.pre_requisitos:

            if pre_requisito not in disciplinas_concluidas:
                raise ValueError(
                    f"Pré-requisito não atendido! O aluno '{aluno.nome}' precisa ser aprovado "
                    f"em '{pre_requisito.nome}' antes de cursar '{turma.curso.nome}'."
                )

        # Avalia se há conflito de dias e horários entre a nova turma e as turmas atuais do aluno.
        if any(turma.verificar_choque_horario(disciplina) for disciplina in disciplinas_ativas):
            raise ValueError(f"Choque de horário detectado entre a turma '{turma.id_turma}' e uma disciplina em curso!")

        # Superadas todas as validações, instancia o vínculo oficial de matrícula (auto-registrado no construtor).
        nova_matricula = Matricula(aluno, turma)

        return nova_matricula


    def salvar_estado(self) -> None:
        """Escreve os dados das listas em memória para um arquivo JSON."""

        pass


    def carregar_estado(self) -> None:
        """Carrega os dados lidos em disco para as listas na memória do sistema."""

        pass


    # Métodos de geração de relatórios acadêmicos.
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

