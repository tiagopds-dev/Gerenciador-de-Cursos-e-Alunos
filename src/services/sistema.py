from src.domain.models.alunos import Aluno
from src.domain.models.turmas import Turma
from src.domain.models.cursos import Curso
from src.domain.models.matriculas import Matricula
from src.domain.models.graduacoes import Graduacao
from src.config.config import Configuracao
from src.repositories.repositorio_aluno import RepositorioAluno
from src.repositories.repositorio_curso import RepositorioCurso
from src.repositories.repositorio_graduacao import RepositorioGraduacao
from src.repositories.repositorio_matricula import RepositorioMatricula
from src.repositories.repositorio_turma import RepositorioTurma


# Construção da classe.
class Sistema:
    """
    Classe principal de controle (Orquestrador).
    Garante o funcionamento da CLI, armazenando as listas de entidades em memória,
    coordenando validações de negócio e delegando a persistência aos repositórios.
    """

    def __init__(self, configuracao: Configuracao) -> None:

        # Atribui e valida a instância de configuração contendo as regras de negócio globais.
        self.configuracao = configuracao

        # Injeção de Dependências: Instancia as ferramentas de conexão com a base de dados (JSON).
        self.__repo_graduacao = RepositorioGraduacao()
        self.__repo_curso = RepositorioCurso()
        self.__repo_turma = RepositorioTurma()
        self.__repo_aluno = RepositorioAluno()
        self.__repo_matricula = RepositorioMatricula()

        # Inicializa as coleções vazias na memória de forma segura para evitar erros de referência.
        self._graduacoes = []
        self._cursos = []
        self._turmas = []
        self._alunos = []
        self._matriculas = []

        # Dispara o gatilho de leitura de todos os dados respeitando a ordem cronológica de dependência.
        self.carregar_estado()


    @property
    def configuracao(self):
        """Retorna as configurações atuais do sistema."""

        return self._configuracao


    @configuracao.setter
    def configuracao(self, nova_configuracao: Configuracao):
        """Define e blinda a injeção das configurações de negócio do sistema."""

        # Garante que apenas um objeto autêntico da classe Configuracao seja injetado.
        if not isinstance(nova_configuracao, Configuracao):
            raise TypeError("A configuração atribuída deve ser um objeto válido da classe 'Configuracao'!")

        self._configuracao = nova_configuracao


    # Propriedades de acesso às listas do sistema (sem setters para evitar sobrescrita acidental).

    @property
    def graduacoes(self):
        return self._graduacoes


    @property
    def cursos(self):
        return self._cursos


    @property
    def turmas(self):
        return self._turmas


    @property
    def alunos(self):
        return self._alunos


    @property
    def matriculas(self):
        return self._matriculas


    # Métodos Orquestradores de Cadastro e Regras de Negócio

    def cadastrar_aluno(self, nome: str, cpf: str, telefone: str, email: str, graduacao: Graduacao) -> None:
        """Adiciona um novo aluno à lista geral da instituição."""

        # Verifica se a graduação pretendida pelo aluno consta nos registros oficiais do sistema.
        if graduacao not in self._graduacoes:
            raise ValueError("A graduação informada para o aluno não está cadastrada no sistema!")

        # Instancia o aluno (acionando internamente as validações de Pessoa e geração de matrícula).
        novo_aluno = Aluno(nome, cpf, telefone, email, graduacao)

        # Registra o novo aluno na coleção em memória do sistema.
        self._alunos.append(novo_aluno)


    def cadastrar_graduacao(self, codigo_mec: str, nome: str, qtd_semestres: int) -> None:
        """Adiciona um novo curso superior à lista de graduações ofertadas pela instituição."""

        # Instancia a nova graduação validando código MEC, nome e duração mínima/máxima.
        nova_graduacao = Graduacao(codigo_mec, nome, qtd_semestres)

        # Registra a nova graduação na coleção em memória do sistema.
        self._graduacoes.append(nova_graduacao)


    def cadastrar_curso(self, nome: str, carga_horaria: int, pre_requisitos: list, ementa: str,
                        graduacao: Graduacao) -> None:
        """Adiciona um novo curso (disciplina) ao catálogo disponível e vincula à graduação."""

        # Impede o cadastro de disciplinas em graduações inexistentes no sistema.
        if graduacao not in self._graduacoes:
            raise ValueError(f"A graduação '{graduacao.nome}' não está cadastrada no sistema!")

        # Instancia o novo curso com as suas regras de carga horária e lista de pré-requisitos.
        novo_curso = Curso(nome, carga_horaria, pre_requisitos, ementa, graduacao)

        # Vincula a disciplina criada diretamente à grade curricular da graduação correspondente.
        graduacao.adicionar_disciplina(novo_curso)

        # Adiciona a disciplina ao catálogo geral de cursos do sistema.
        self._cursos.append(novo_curso)


    def abrir_turma(self, periodo: str, dias_horarios: dict, vagas: int, local: str, curso: Curso) -> None:
        """Adiciona uma nova oferta de turma vinculada a um curso específico e ativa-a no sistema."""

        # Garante que o curso ofertado pertença ao catálogo oficial do sistema.
        if curso not in self._cursos:
            raise ValueError(f"O curso '{curso.nome}' não está cadastrado no catálogo do sistema!")

        # Instancia a turma (o construtor da Turma já a vincula automaticamente ao Curso e gera o ID).
        nova_turma = Turma(periodo, dias_horarios, vagas, local, curso)

        # Registra a nova oferta na lista geral de turmas ativas do sistema.
        self._turmas.append(nova_turma)


    def realizar_matricula(self, aluno: Aluno, turma: Turma) -> None:
        """Localiza as instâncias, executa uma rigorosa bateria de validações e vincula o Aluno à Turma."""

        # Verifica se o aluno informado pertence aos registros ativos da instituição.
        if aluno not in self._alunos:
            raise ValueError(f"O aluno '{aluno.nome}' não está cadastrado no sistema!")

        # Verifica se a turma informada consta nas ofertas oficiais da instituição.
        if turma not in self._turmas:
            raise ValueError(f"A turma '{turma.id_turma}' não está cadastrada no sistema!")

        # Impede matrículas em turmas que já foram encerradas, canceladas ou trancadas.
        if turma.status != "Aberta":
            raise ValueError(
                f"A matrícula não pode ser realizada pois a turma '{turma.id_turma}' está '{turma.status}'!")

        # Verifica a disponibilidade de vagas comparando matrículas ativas na turma com o seu limite máximo.
        if len(turma.matriculas_ativas) >= turma.vagas:
            raise ValueError(f"A turma '{turma.id_turma}' já atingiu o limite máximo de {turma.vagas} vagas!")

        # Extrai de forma rápida todas as turmas que o aluno já está cursando atualmente.
        disciplinas_ativas = {
            matricula.turma
            for matricula in aluno.historico
            if matricula.status == "Cursando"
        }

        # Extrai de forma rápida todos os cursos (disciplinas) nos quais o aluno já obteve aprovação.
        disciplinas_concluidas = {
            matricula.turma.curso
            for matricula in aluno.historico
            if matricula.status == "Aprovado"
        }

        # Impede que o aluno curse novamente uma disciplina que já está em andamento ou que já concluiu.
        if turma in disciplinas_ativas or turma.curso in disciplinas_concluidas:
            raise ValueError(f"O aluno '{aluno.nome}' já está cursando ou já foi aprovado em '{turma.curso.nome}'!")

        # Verifica se o aluno atingiu o teto de disciplinas simultâneas permitido pelo documento de configuração.
        if len(disciplinas_ativas) >= self.configuracao.max_turmas