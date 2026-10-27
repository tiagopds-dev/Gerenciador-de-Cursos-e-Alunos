from src.domain.models.alunos import Aluno
from src.domain.models.turmas import Turma
from src.domain.models.cursos import Curso
from src.domain.models.matriculas import Matricula
from src.domain.models.graduacoes import Graduacao
from config.config import Configuracao


class Sistema:
    """
    Classe principal de controle. Garante o funcionamento da CLI, armazenando as listas
    (graduações, cursos, turmas, alunos) em memória, coordenando cadastros e matrículas.
    """

    def __init__(self, configuracao: Configuracao) -> None:
        self.configuracao = configuracao

        self._alunos = []
        self._turmas = []
        self._cursos = []
        self._graduacoes = []


    @property
    def configuracao(self):
        return self._configuracao


    @configuracao.setter
    def configuracao(self, nova_configuracao: Configuracao):
        if not isinstance(nova_configuracao, Configuracao):
            raise TypeError
        self._configuracao = nova_configuracao


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


    def cadastrar_aluno(self, nome: str, cpf: str, telefone: str, email: str, graduacao: Graduacao) -> None:
        """Adiciona um novo aluno à lista geral de alunos matriculados na instituição."""

        novo_aluno = Aluno(nome, cpf, telefone, email, graduacao)
        self._alunos.append(novo_aluno)


    def cadastrar_graduacao(self, codigo_mec: str, nome: str, qtd_semestres: int) -> None:
        """Adiciona um novo curso superior à lista de graduações ofertadas pela instituição."""

        nova_graduacao = Graduacao(codigo_mec, nome, qtd_semestres)
        self._graduacoes.append(nova_graduacao)


    def cadastrar_curso(self, nome: str, carga_horaria: int, pre_requisitos: list, ementa: str, graduacao: Graduacao) -> None:
        """Adiciona um novo curso (disciplina) ao catálogo disponível do sistema."""

        if graduacao not in self._graduacoes:
            raise ValueError

        novo_curso = Curso(nome, carga_horaria, pre_requisitos, ementa, graduacao)
        graduacao.adicionar_disciplina(novo_curso)
        self._cursos.append(novo_curso)


    def abrir_turma(self, periodo: str, dias_horarios: dict, vagas: int, local: str, curso: Curso) -> None:
        """Adiciona uma nova oferta de turma à lista de turmas ativas."""

        if curso not in self._cursos:
            raise ValueError

        nova_turma = Turma(periodo, dias_horarios, vagas, local, curso)
        self._turmas.append(nova_turma)

    def realizar_matricula(self, aluno: Aluno, turma: Turma) -> None:
        """Localiza as instâncias e realiza as validações (choque, vagas, pré-requisitos) para criar uma Matrícula."""

        if aluno not in self._alunos:
            raise ValueError

        if turma not in self._turmas:
            raise ValueError

        if turma.status != "Aberta":
            raise ValueError

        if len(turma.matriculas_ativas) >= turma.vagas:
            raise ValueError

        disciplinas_ativas = {
            matricula.turma
            for matricula in aluno.historico
            if matricula.status == "Cursando"
        }

        if len(disciplinas_ativas) >= self.configuracao.max_turmas_por_aluno:
            raise ValueError

        if any(turma.verificar_choque_horario(disciplina) for disciplina in disciplinas_ativas):
            raise ValueError("Choque de horário com uma disciplina em curso!")

        disciplinas_concluidas = {
            matricula.turma.curso
            for matricula in aluno.historico
            if matricula.status == "Aprovado"
        }

        for pre_requisito in turma.curso.pre_requisitos:
            if pre_requisito not in disciplinas_concluidas:
                raise ValueError

        if turma in disciplinas_ativas or turma.curso in disciplinas_concluidas:
            raise ValueError

        # Se passou por tudo, a mágica acontece:
        nova_matricula = Matricula(aluno, turma)
        turma.matriculas_ativas.append(nova_matricula)
        aluno.historico.append(nova_matricula)


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
