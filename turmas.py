from ofertas import Oferta

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

    def verificar_choque_horario(self, outra_turma: 'Turma') -> bool:
        """Verifica se os horários desta turma conflitam com os de uma turma já matriculada."""
        pass