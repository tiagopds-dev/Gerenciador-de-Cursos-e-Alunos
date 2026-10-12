from datetime import date
from config import Configuracao
from alunos import Aluno
from turmas import Turma
import re

class Matricula:
    """
    Classe associativa que conecta um Aluno a uma Turma. Guarda as notas, a frequência 
    e atualiza o status de aprovação com base nas regras do sistema.
    """

    # Atributo de classe privado e imutável (tupla)
    _STATUS_VALIDOS = ("Cursando", "Trancada", "Reprovado por Falta", "Reprovado por Nota", "Reprovado por Falta e por Nota", "Aprovado")

    def __init__(self, aluno: Aluno, turma: Turma) -> None:

        # Inicializa as notas como um dicionário vazio (momento da criação)
        self.notas = {
            'AV1': None,
            'AV2': None,
            'MF': None
        }
            
        # Inicializa as horas frequentadas como zero (momento da criação)
        self._horas_frequentadas = 0

        # Inicializa a matrícula com um status automático no momento da criação
        self.status = "Cursando"

        # Recebe um objeto do tipo Aluno para realizar a associação
        self.aluno = aluno

        # Recebe um objeto do tipo Turma para realizar a associação
        self.turma = turma


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def notas(self):
        return self._notas


    # Transforma a atribuição num Setter com validação obrigatória
    @notas.setter
    def notas(self, notas):

        # Verifica se o valor passado é um dicionário
        if not isinstance(notas, dict):
            raise TypeError

        # Caso seja, realiza a atribuição de forma segura
        self._notas = notas


    # Como a frequencia será sempre atualizada de forma automática, não será criado um setter
    # Dessa forma, não haverá como atribuir diretamente uma frequencia após a criação (apenas leitura)
    # Retorna o percentual de presença diretamente com base na carga horária
    @property
    def frequencia(self):
        return (self._horas_frequentadas / self.turma.curso.carga_horaria) * 100


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def status(self):
        return self._status


    # Transforma a atribuição num Setter com validação obrigatória
    @status.setter
    def status(self, status):

        # Impede a alteração caso o status passado não pertença a lista de status aceitos
        if status not in Matricula._STATUS_VALIDOS:
            raise Exception("Status de matrícula inválido!")

        # Caso contrário, a atribuição é feita
        self._status = status

        
    def lancar_nota(self, nome_nota: str, nota: float) -> None:
        """Adiciona uma nova nota validada à lista de notas do aluno nesta turma."""

        # Verifica se os tipos de dados passados nos parâmetros do método foram corretos (blindagem contra booleano)
        if not isinstance(nome_nota, str) or isinstance(nota, bool) or not isinstance(nota, (float, int)):
            raise TypeError

        # Impede a adição da nota caso o nome da nota esteja vazio
        if not nome_nota:
            raise Exception("O nome da nota não pode estar vazio!")

        # Higieniza a string passada como nome da nota
        nome_nota = re.sub(r'[^a-zA-Z0-9]', '', nome_nota).upper()

        # Barra a adição da nota caso o nome da nota não se iguale aos padrões pré-definidos
        if nome_nota != "AV1" and nome_nota != "AV2":
            raise Exception("Nome de avaliação inválido!")

        # Proibe a adição da nota caso o valor passado não esteja no intervalo pré-definido
        if nota < 0 or nota > 10:
            raise Exception("Nota inválida!")

        # Caso todas as validações sejam atendidas, a nota é adicionada
        self.notas[nome_nota] = float(nota)

        # Faz o recáculo inteligente da média somente após as duas notas tiverem sido adicionadas
        if self.notas['AV1'] is not None and self.notas['AV2'] is not None:
            self.notas['MF'] = round(((self.notas['AV1'] + self.notas['AV2']) / 2), 2)
    
    
    def lancar_frequencia(self, horas: int = 2) -> None:
        """Atualiza a porcentagem de frequência do aluno."""

        # Verifica se o tipo de dado passado nos parâmetro do método foi correto (blindagem contra booleano)
        if isinstance(horas, bool) or not isinstance(horas, int):
            raise TypeError
        
        # Impede a atualização da carga horária frequentada caso o valor das horas-aula passado seja zero
        if horas <= 0:
            raise Exception("A quantidade de horas-aula não pode ser menor ou igual a zero!")

        # Atribui o novo valor da carga horária frequentada numa variável auxiliar para verificação
        horas_totais = self._horas_frequentadas + horas

        # Barra a atualização da carga horária frequentada caso as horas totais ultrapassem o valor da carga horária total da turma
        if horas_totais > self.turma.curso.carga_horaria:
            raise Exception("A quantidade de horas frequentadas não pode ser maior que a carga horária total da turma!")  

        # Caso todas as verificações sejam atendidas, atualiza o valor da carga horária frequentada
        self._horas_frequentadas += horas
        

    def atualizar_situacao(self, regras: Configuracao) -> None:
        """Calcula a situação final do aluno com base nas notas, frequência e regras vigentes."""

        # Impede a alteração de status caso aluno tenha a matrícula trancada
        if self.status == "Trancada":
            raise Exception("Aluno não elegível a alteração de status. Matrícula trancada!")

        # Barra a alteração de status caso o aluno não possua as duas notas consolidadas no sistema
        if self.notas['MF'] is None:
            raise Exception("Aluno não elegível a alteração de status. Notas pendentes!")

        # Reprova por falta caso o aluno atinja a nota mínima, mas não cumpra a frequência exigida
        if self.frequencia < regras.frequencia_minima_aprovacao and self.notas['MF'] >= regras.nota_minima_aprovacao:
            self.status = "Reprovado por Falta"

        # Reprova por nota caso o aluno tenha frequência suficiente, mas não atinja a média mínima
        elif self.frequencia >= regras.frequencia_minima_aprovacao and self.notas['MF'] < regras.nota_minima_aprovacao:
            self.status = "Reprovado por Nota"

        # Reprova por ambos os critérios caso o aluno não atinja nem a frequência nem a nota mínima
        elif self.frequencia < regras.frequencia_minima_aprovacao and self.notas['MF'] < regras.nota_minima_aprovacao:
            self.status = "Reprovado por Falta e por Nota"

        # Caso passe por todas as verificações de reprovação, o aluno cumpre todos os requisitos e é aprovado
        else:
            self.status = "Aprovado"
        

    def trancar_matricula(self, regras: Configuracao) -> None:
        """Valida e processa a desistência da disciplina dentro do prazo estipulado."""

        # Impede a alteração de status caso o aluno já tenha a matrícula trancada
        if self.status == "Trancada":
            raise Exception("Aluno não elegível a alteração de status. Matrícula já está trancada!")

        # Barra a alteração de status caso o aluno já tenha sido aprovado na disciplina
        if self.status == "Aprovado":
            raise Exception("Aluno não elegível a alteração de status. Processo de aprovação na disciplina já concluído!")
        
        # Bloqueia a alteração de status caso o aluno já tenha sido reprovado na disciplina
        if self.status in ("Reprovado por Falta", "Reprovado por Nota", "Reprovado por Falta e por Nota"):
            raise Exception("Aluno não elegível a alteração de status. Processo de avaliação na disciplina já concluído!")

        # Captura a data atual do sistema para comparar com a data limite estabelecida para trancamento
        data_atual = date.today()

        # Restringe a alteração de status caso o período limite de trancamento já tenha passado
        if data_atual > regras.data_limite_trancamento:
            raise Exception("Aluno não elegível a alteração de status. Período de trancamento fechado!")

        # Caso passe por todas as verificações estabelecidas, o aluno cumpre todos os requisitos e tem sua matrícula trancada
        self.status = "Trancada"