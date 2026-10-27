import re
from datetime import date
from typing import TYPE_CHECKING

# Permite importar as classes estritamente para realizar o Type Hinting.
# Resolve os alertas da IDE sem causar o erro fatal de importação circular em tempo real.
if TYPE_CHECKING:
    from src.domain.models.alunos import Aluno
    from src.domain.models.turmas import Turma
    from config.config import Configuracao


# Construção da classe.
class Matricula:
    """
    Classe associativa que conecta um Aluno a uma Turma. Guarda as notas, a frequência
    e atualiza a situação de aprovação com base nas regras do sistema.
    """

    # Atributo de classe privado e imutável (tupla).
    _STATUS_VALIDOS = (
        "Cursando",
        "Trancada",
        "Reprovado por Falta",
        "Reprovado por Nota",
        "Reprovado por Falta e por Nota",
        "Aprovado"
    )


    def __init__(self, aluno: "Aluno", turma: "Turma") -> None:

        # Validação estrita de tipo para evitar quebra de sistema.
        if aluno.__class__.__name__ != "Aluno":
            raise TypeError("O aluno vinculado deve ser um objeto válido da classe 'Aluno'!")

        if turma.__class__.__name__ != "Turma":
            raise TypeError("A turma vinculada deve ser um objeto válido da classe 'Turma'!")

        # Recebe os objetos associativos.
        self.aluno = aluno

        self.turma = turma

        # Inicializa as notas como um dicionário com chaves pré-definidas.
        self.notas = {
            "AV1": None,
            "AV2": None,
            "MF": None
        }

        # Inicializa as horas frequentadas como zero.
        self._horas_frequentadas = 0

        # Passa pelo setter para garantir que a situação inicial é válida.
        self.status = "Cursando"

        # Registra esta matrícula na lista de matrículas ativas da turma.
        self.turma.matriculas_ativas.append(self)

        # Registra a matrícula no histórico acadêmico do aluno.
        self.aluno.historico.append(self)


    @property
    def notas(self):
        return self._notas


    @notas.setter
    def notas(self, notas: dict):

        if not isinstance(notas, dict):
            raise TypeError("As notas devem ser armazenadas em um formato de dicionário!")

        self._notas = notas


    @property
    def frequencia(self) -> float:
        """Retorna o percentual de presença com base na carga horária da disciplina."""

        # A carga horária da turma já está blindada contra valores nulos/negativos na classe Curso.
        percentual = (self._horas_frequentadas / self.turma.curso.carga_horaria) * 100

        return round(percentual, 2)


    @property
    def status(self):
        return self._status


    @status.setter
    def status(self, novo_status: str):

        if not isinstance(novo_status, str):
            raise TypeError("O status da matrícula deve ser enviado em formato de texto!")

        if novo_status not in Matricula._STATUS_VALIDOS:
            raise ValueError(
                f"Status '{novo_status}' inválido! Os status permitidos são: {', '.join(Matricula._STATUS_VALIDOS)}."
            )

        self._status = novo_status


    def lancar_nota(self, nome_nota: str, nota: float) -> None:
        """Adiciona uma nova nota validada à lista de notas do aluno nesta turma."""

        if not isinstance(nome_nota, str):
            raise TypeError("O nome da avaliação deve ser enviado em formato de texto!")

        if isinstance(nota, bool) or not isinstance(nota, (float, int)):
            raise TypeError("A nota deve ser um valor numérico!")

        if not nome_nota.strip():
            raise ValueError("O nome da avaliação não pode estar vazio!")

        # Higieniza a string passada como nome da nota.
        nome_nota_limpa = re.sub(r"[^a-zA-Z0-9]", "", nome_nota).upper()

        if nome_nota_limpa not in ["AV1", "AV2"]:
            raise ValueError(f"Nome de avaliação inválido ('{nome_nota_limpa}')! Utilize 'AV1' ou 'AV2'.")

        if nota < 0 or nota > 10:
            raise ValueError(f"Nota inválida ({nota})! A nota deve ser um valor entre 0 e 10.")

        # Caso todas as validações sejam atendidas, a nota é adicionada.
        self.notas[nome_nota_limpa] = float(nota)

        # Faz o recálculo inteligente da média somente após as duas notas terem sido adicionadas.
        av1, av2 = self.notas["AV1"], self.notas["AV2"]

        # Se nenhuma for nula, calcula a média.
        if av1 is not None and av2 is not None:
            self.notas["MF"] = round((av1 + av2) / 2, 2)


    def lancar_frequencia(self, horas: int = 2) -> None:
        """Atualiza a porcentagem de frequência do aluno com as horas-aula assistidas."""

        if isinstance(horas, bool) or not isinstance(horas, int):
            raise TypeError("As horas frequentadas devem ser informadas como um número inteiro!")

        if horas <= 0:
            raise ValueError(f"A quantidade de horas-aula deve ser maior que zero! Valor recebido: {horas}h.")

        horas_totais = self._horas_frequentadas + horas

        carga_total_curso = self.turma.curso.carga_horaria

        if horas_totais > carga_total_curso:
            raise ValueError(
                f"Limite excedido! "
                f"As horas frequentadas ({horas_totais}h) não podem ultrapassar a carga horária da disciplina ({carga_total_curso}h)."
            )

        self._horas_frequentadas += horas


    def atualizar_situacao(self, regras: "Configuracao") -> None:
        """Calcula a situação final do aluno com base nas notas, frequência e regras vigentes."""

        if regras.__class__.__name__ != "Configuracao":
            raise TypeError("As regras devem ser um objeto válido da classe 'Configuracao'!")

        if self.status == "Trancada":
            raise ValueError(
                f"O aluno '{self.aluno.nome}' possui a matrícula trancada e não é elegível à consolidação final!"
            )

        # Se a MF for None (aluno abandonou/não fez provas), 0.0 é assumido para o cálculo.
        nota_final = self.notas.get("MF")

        if nota_final is None:
            nota_final = 0.0

        # Avaliação das regras de negócio para verificação situacional do aluno.
        reprovado_falta = self.frequencia < regras.frequencia_minima

        reprovado_nota = nota_final < regras.nota_minima_aprovacao

        if reprovado_falta and not reprovado_nota:
            self.status = "Reprovado por Falta"

        elif not reprovado_falta and reprovado_nota:
            self.status = "Reprovado por Nota"

        elif reprovado_falta and reprovado_nota:
            self.status = "Reprovado por Falta e por Nota"

        else:
            self.status = "Aprovado"


    def trancar_matricula(self, regras: "Configuracao") -> None:
        """Valida e processa a desistência da disciplina dentro do prazo estipulado."""

        if regras.__class__.__name__ != "Configuracao":
            raise TypeError("As regras devem ser um objeto válido da classe 'Configuracao'!")

        if self.status == "Trancada":
            raise ValueError(f"A matrícula do aluno '{self.aluno.nome}' já se encontra trancada!")

        if self.status != "Cursando":
            raise ValueError(
                f"Não é possível trancar a matrícula! "
                f"O status atual é '{self.status}', indicando que a disciplina já foi encerrada para este aluno."
            )

        # Captura a data atual do sistema para comparar com a data limite.
        data_atual = date.today()

        if data_atual > regras.data_limite_trancamento:
            # Formata a data ('DD/MM/AAAA') para exibir na mensagem de erro amigável.
            raise ValueError(
                f"Período de trancamento encerrado! A data limite era '{regras.data_limite_trancamento.strftime('%d/%m/%Y')}'."
            )

        # Tranca a matrícula.
        self.status = "Trancada"

        # Remove o aluno da lista de matrículas ativas da turma de forma segura.
        if self in self.turma.matriculas_ativas:
            self.turma.matriculas_ativas.remove(self)