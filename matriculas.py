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

    def __init__(self, aluno: Aluno, turma: Turma) -> None:

        # Inicializa as notas como um dicionário vazio (momento da criação)
        self.notas = {
            'AV1': 0,
            'AV2': 0,
            'MF': round((self.notas['AV1'] + self.notas['AV2']) / 2)
        }
            
        # Inicializa as horas frequentadas como zero (momento da criação)
        self._horas_frequentadas = 0


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
    def matricula(self):
        return (self._horas_frequentadas / self.turma.curso.carga_horaria) * 100
    
        
    def lancar_nota(self, nome_nota: str, nota: float) -> None:
        """Adiciona uma nova nota validada à lista de notas do aluno nesta turma."""

        # Verifica se o tipos de dado passado nos parâmetros do método foram corretos
        if not isinstance(nome_nota, str) or not isinstance(nota, float):
            raise TypeError

        # Impede a adição da nota caso o nome da nota esteja vazio
        if not nome_nota:
            raise Exception("O nome da nota não pode estar vazio!")

        # Higieniza a string passada como nome da nota
        nome_nota = re.sub(r'[^a-zA-Z0-9]', '', nome_nota).upper()

        # Barra a adição da nota caso o nome da nota não se iguale aos padrões pré-definidos
        if nome_nota != "AV1" or nome_nota != "AV2":
            raise Exception("Nome de avaliação inválido!")

        # Proibe a adição da nota caso o valor passado não esteja no intervalo pré-definido
        if 0 > nota > 10:
                raise Exception("Nota inválida!")

        # Caso todas as validações sejam atendidas, a nota é adicionada
        self.nota[nome] = nota
    
    
    def lancar_frequencia(self, horas: int = 2) -> None:
        """Atualiza a porcentagem de frequência do aluno."""

        # Verifica se o tipo de dado passado nos parâmetro do método foi correto
        if not isinstance(horas, int):
            raise TypeError
        
        # Impede a atualização da carga horária frequentada caso o valor das horas-aula passado seja zero
        if horas <= 0:
            raise Exception("A quantidade de horas-aula não pode ser menor ou igual a zero!")

        # Atribui o novo valor da carga horária frequentada numa variável auxiliar para verificação
        horas_totais = self._horas_frequentadas + horas

        # Barra a atualização da carga horária frequentada caso as horas totais ultrapassem o valor da carga horária total da turma
        if horas_totais > self.turma.curso.carga_horaria:
            raise Exception("A quantidade de horas frequentadas não pode ser maior que a cagar horária total da turma!")  

        # Caso todas as verificações sejam atendidas, atualiza o valor da carga horária frequentada
        self._horas_frequentadas += horas
        

    def atualizar_situacao(self, regras: 'Configuracao') -> None:
        """Calcula a situação final do aluno com base nas notas, frequência e regras vigentes."""
        pass

    def trancar_matricula(self, data_atual: date, data_limite: date) -> bool:
        """Valida e processa a desistência da disciplina dentro do prazo estipulado."""
        pass