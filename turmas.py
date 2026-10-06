from ofertas import Oferta
import re
from cursos import Curso

class Turma(Oferta):
    """
    Herda de Oferta e concretiza a oferta de um Curso específico em um semestre. 
    Controla o próprio status (aberta/fechada) e possui a lógica contra choques de horário.
    """

    # Cria um atributo de classe que atua como contador sequencial
    # Pertence à classe Turma, assim, não é resetado a cada novo objeto
    _contador_turma = 1

    def __init__(self, periodo: str, dias_horarios: dict, vagas: int, local: str, curso: Curso) -> None:
        super().__init__(periodo, dias_horarios, vagas, local)

        # Armazena apenas os dígitos do período da turma
        periodo_limpo = re.sub(r'[^0-9]', '', self.periodo)

        # Gera um ID de turma automático utilizando um padrão pré-estabelecido
        # (Período da turma + Identificador único da turma)
        # :02d força o número a ter 2 casas, preenchendo com zeros à esquerda
        self._id_turma = f"{periodo_limpo}{Turma._contador_turma:02d}"

        # Incrementa o contador da classe para a próxima turma que for criada
        Turma._contador_turma += 1
        
        # Inicializa a lista de matrículas ativas como uma lista vazia (momento da criação)
        self._matriculas_ativas = []

        # Atribui o curso como atributo vinculado diretamente a uma turma
        self.curso = curso

        # Define automaticamente o status de "aberto" para uma turma criada
        self.abrir_turma()
        


    # Como o ID da turma será gerado sempre de forma automática, não será criado um setter
    # Dessa forma, não haverá como alterar o ID da turma após a criação (apenas leitura)
    @property
    def id_turma(self):
        return self._id_turma

    
    # Permite leitura e modificações internas na lista (ex: .append), 
    # mas a ausência do Setter impede a substituição acidental de todo o histórico de matrículas ativas
    @property
    def matriculas_ativas(self):
        return self._matriculas_ativas


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def status(self):
        return self._status


    # Transforma a atribuição num Setter com validação obrigatória
    @status.setter
    def status(self, status):

        # Verifica se um status inválido foi passado
        if status != "Aberta" and status != "Fechada":
            raise Exception("Status inválido!")

        # Caso contrário, recebe novo status
        self._status = status



    def abrir_turma(self) -> None:
        """Altera o status da turma para 'Aberta'."""

        # Proibe alteração de status caso turma já esteja aberta
        if self.status == "Aberta":
            raise Exception(f"Operação inválida. Status atual da turma: {self.status}!")

        # Barra a alteração de status caso a turma já esteja fechada e cheia
        if self.status == "Fechada" and len(self.matriculas_ativas):
            raise Exception(f"Operação inválida. Turma cheia!")

        self.status = "Aberta"


    def fechar_turma(self) -> None:
        """Altera o status da turma para 'Fechada', impedindo novas matrículas."""
        pass

    def verificar_choque_horario(self, outra_turma: 'Turma') -> bool:
        """Verifica se os horários desta turma conflitam com os de uma turma já matriculada."""
        pass