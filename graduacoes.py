from cursos import Curso
from matriculas import Matricula


class Graduacao:
    """
    Representa o curso superior do mundo real.
    Atua como um agrupador lógico, guardando a grade curricular de disciplinas exigidas.
    """
    def adicionar_disciplina(self, disciplina: 'Curso') -> None:
        """Insere um novo objeto Curso na lista da grade curricular."""
        pass

    def calcular_carga_horaria_total(self) -> int:
        """Varre a grade curricular somando a carga horária de todos os cursos vinculados."""
        pass

    def verificar_elegibilidade_formatura(self, historico_aluno: list['Matricula']) -> bool:
        """Compara o histórico do aluno com a grade curricular para determinar se ele pode colar grau."""
        pass