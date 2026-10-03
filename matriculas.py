from datetime import date
from config import Configuracao

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

    def atualizar_situacao(self, regras: 'Configuracao') -> None:
        """Calcula a situação final do aluno com base nas notas, frequência e regras vigentes."""
        pass

    def trancar_matricula(self, data_atual: date, data_limite: date) -> bool:
        """Valida e processa a desistência da disciplina dentro do prazo estipulado."""
        pass