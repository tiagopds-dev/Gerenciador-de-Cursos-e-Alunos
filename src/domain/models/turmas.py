import re
from typing import TYPE_CHECKING
from src.domain.models.ofertas import Oferta

# Permite importar as classes estritamente para realizar o Type Hinting.
# Resolve os alertas da IDE sem causar o erro fatal de importação circular em tempo real.
if TYPE_CHECKING:
    from src.domain.models.cursos import Curso
    from src.config.config import Configuracao


# Construção da classe.
class Turma(Oferta):
    """
    Herda de Oferta e concretiza a oferta de um Curso específico em um semestre.
    Controla a própria condição (aberta/fechada) e possui a lógica contra choques de horário.
    """

    # Cria um atributo de classe que atua como contador sequencial.
    # Pertence à classe Turma, assim, não é reinicializado a cada novo objeto.
    _contador_turma = 1


    def __init__(self, periodo: str, dias_horarios: dict, vagas: int, local: str, curso: "Curso") -> None:

        # Chama o construtor da superclasse Oferta para validar e atribuir os dados base.
        super().__init__(periodo, dias_horarios, vagas, local)

        # Validação de segurança para garantir que o objeto passado é um Curso válido.
        if curso.__class__.__name__ != "Curso":
            raise TypeError("O curso vinculado deve ser um objeto válido da classe Curso!")

        # Armazena apenas os dígitos do período da turma.
        periodo_limpo = re.sub(r"[^0-9]", "", self.periodo)

        # Gera um ID de turma automático utilizando um padrão pré-estabelecido.
        # (Período da turma + Identificador único da turma).
        # ':02d' força o número a ter 2 casas, preenchendo com zeros à esquerda.
        self._id_turma = f"{periodo_limpo}{Turma._contador_turma:02d}"

        # Incrementa o contador da classe para a próxima turma que for criada.
        Turma._contador_turma += 1

        # Inicializa a lista de matrículas ativas como uma lista vazia (momento da criação).
        self._matriculas_ativas = []

        # Atribui o curso como atributo vinculado diretamente a uma turma.
        self.curso = curso

        # Define automaticamente a condição de 'Aberta' para uma turma recém-criada.
        self.status = "Aberta"

        # Adiciona a turma criada no histórico de turmas ofertadas do curso correspondente.
        self.curso.vincular_turma(self)


    # Como o ID da turma será gerado sempre de forma automática, não será criado um setter.
    # Dessa forma, não haverá como alterar o ID da turma após a criação (apenas leitura).
    @property
    def id_turma(self):
        return self._id_turma


    # Permite leitura e modificações internas na lista (ex: '.append'),
    # mas a ausência do Setter impede a substituição acidental do histórico de matrículas ativas.
    @property
    def matriculas_ativas(self):
        return self._matriculas_ativas


    @property
    def status(self):
        return self._status


    @status.setter
    def status(self, novo_status: str):

        if not isinstance(novo_status, str):
            raise TypeError("O status da turma deve ser enviado em formato de texto!")

        # Verifica se uma condição inválida foi passada, detalhando as opções corretas.
        if novo_status not in ["Aberta", "Fechada"]:
            raise ValueError(f"Status inválido ('{novo_status}')! A turma só pode estar 'Aberta' ou 'Fechada'.")

        self._status = novo_status


    def abrir_turma(self, configuracao: "Configuracao") -> None:
        """Altera a situação da turma para 'Aberta'."""

        if configuracao.__class__.__name__ != "Configuracao":
            raise TypeError("A configuração deve ser um objeto válido da classe Configuracao!")

        # Proíbe alteração de condição caso turma já esteja aberta.
        if self.status == "Aberta":
            raise ValueError(f"A turma '{self.id_turma}' já se encontra Aberta!")

        # Barra a alteração de condição caso a turma já esteja fechada e cheia.
        if self.status == "Fechada" and len(self.matriculas_ativas) >= self.vagas:
            raise ValueError(
                f"Não é possível reabrir a turma '{self.id_turma}': o limite de {self.vagas} vagas já foi atingido!"
            )

        # Impede a alteração de condição caso o período fornecido seja anterior ao período atual.
        if self.periodo < configuracao.semestre_vigente:
            raise ValueError(
                f"Não é possível abrir uma turma de um período passado ('{self.periodo}')! "
                f"O semestre vigente é '{configuracao.semestre_vigente}'."
            )

        # Se todas as verificações forem atendidas, a turma será aberta.
        self.status = "Aberta"


    def fechar_turma(self) -> None:
        """Altera a situação da turma para 'Fechada', impedindo novas matrículas."""

        # Proíbe alteração de condição caso turma já esteja fechada.
        if self.status == "Fechada":
            raise ValueError(f"A turma '{self.id_turma}' já se encontra Fechada!")

        # Barra a alteração de condição caso o número mínimo de matrículas ativas não tenha sido atingido.
        if len(self.matriculas_ativas) < 5:
            raise ValueError(
                f"A turma '{self.id_turma}' não atingiu o quórum mínimo de 5 alunos (Atuais: {len(self.matriculas_ativas)})!"
            )

        # Impede o fechamento se houver matrículas não consolidadas.
        if any(matricula.status == "Cursando" for matricula in self.matriculas_ativas):
            raise ValueError(
                f"Não é possível fechar a turma '{self.id_turma}'. "
                f"Ainda há alunos com o status 'Cursando'!"
            )

        # Se todas as verificações forem atendidas, a turma será fechada.
        self.status = "Fechada"


    def verificar_choque_horario(self, outra_turma: "Turma") -> bool:
        """Verifica se os horários desta turma conflitam com os de uma turma já matriculada."""

        if outra_turma.__class__.__name__ != "Turma":
            raise TypeError("A turma para comparação deve ser um objeto válido da classe Turma!")

        # Tenta encontrar os pares dia-horário que são exatamente iguais em ambas as turmas.
        horarios_comuns = self.dias_horarios.items() & outra_turma.dias_horarios.items()

        # Retorna verdadeiro se houver conflito, falso caso contrário (avaliando diretamente a existência de itens).
        return bool(horarios_comuns)