from graduacoes import Graduacao
from cursos import Curso
from alunos import Aluno
from turmas import Turma


class Sistema:
    """
    Classe principal de controle. Garante o funcionamento da CLI, armazenando as listas 
    (graduações, cursos, turmas, alunos) em memória, coordenando cadastros e matrículas.
    """
    def cadastrar_graduacao(self, graduacao: Graduacao) -> None:
        """Adiciona um novo curso superior à lista de graduações ofertadas pela instituição."""
        pass

    def cadastrar_curso(self, curso: Curso) -> None:
        """Adiciona um novo curso (disciplina) ao catálogo disponível do sistema."""
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
