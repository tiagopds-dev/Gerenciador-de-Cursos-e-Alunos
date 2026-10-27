import re
from typing import TYPE_CHECKING

# Permite importar as classes estritamente para realizar o Type Hinting.
# Resolve os alertas da IDE sem causar o erro fatal de importação circular em tempo real.
if TYPE_CHECKING:
    from src.domain.models.cursos import Curso
    from src.domain.models.matriculas import Matricula


# Construção da classe.
class Graduacao:
    """
    Representa o curso superior do mundo real.
    Atua como um agrupador lógico, guardando a grade curricular de disciplinas exigidas.
    """


    def __init__(self, codigo_mec: str, nome: str, qtd_semestres: int) -> None:

        self.codigo_mec = codigo_mec

        self.nome = nome

        self.qtd_semestres = qtd_semestres

        # Inicializa o histórico como uma lista vazia de cursos (momento da criação).
        self._grade_curricular = []


    @property
    def codigo_mec(self):
        return self._codigo_mec


    @codigo_mec.setter
    def codigo_mec(self, novo_codigo: str):

        if not isinstance(novo_codigo, str):
            raise TypeError("O código MEC deve ser uma string!")

        # Retira quaisquer coisas que não sejam dígitos (0-9).
        novo_codigo = re.sub(r"[^0-9]", "", novo_codigo)

        # Valida tamanho exato do argumento passado para código.
        if not novo_codigo or len(novo_codigo) != 8:
            raise ValueError("O código MEC deve conter exatamente 8 dígitos numéricos!")

        self._codigo_mec = novo_codigo


    @property
    def nome(self):
        return self._nome


    @nome.setter
    def nome(self, novo_nome: str):

        if not isinstance(novo_nome, str):
            raise TypeError("O nome da graduação deve ser uma string!")

        # Retira caracteres inválidos e transforma tudo em minúsculas para criar a base.
        novo_nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", novo_nome).lower()

        if not novo_nome or len(novo_nome) < 6:
            raise ValueError("O nome da graduação deve conter pelo menos 6 letras válidas!")

        # Lista de exceções.
        excecoes = {"de", "da", "do", "das", "dos", "a", "e", "o", "as", "os", "em", "por", "para", "com"}

        # Formatação inteligente usando List Comprehension.
        # Capitaliza a primeira palavra (índice 0) OU se a palavra NÃO estiver nas exceções.
        palavras = [
            p.capitalize() if i == 0 or p not in excecoes else p
            for i, p in enumerate(novo_nome.split())
        ]

        self._nome = " ".join(palavras)


    @property
    def qtd_semestres(self):
        return self._qtd_semestres


    @qtd_semestres.setter
    def qtd_semestres(self, nova_quantidade: int):

        if not isinstance(nova_quantidade, int) or isinstance(nova_quantidade, bool):
            raise TypeError("A quantidade de semestres deve ser um número inteiro!")

        if nova_quantidade < 3 or nova_quantidade > 12:
            raise ValueError("A graduação deve ter entre 3 e 12 semestres de duração!")

        self._qtd_semestres = nova_quantidade


    @property
    def grade_curricular(self):
        return self._grade_curricular


    # O uso de 'Curso' em formato de string (Forward Reference) na tipagem protege a IDE.
    def adicionar_disciplina(self, disciplina: "Curso") -> None:
        """Insere um novo objeto Curso na lista da grade curricular."""

        if disciplina.__class__.__name__ != "Curso":
            raise TypeError("Apenas objetos da classe Curso podem ser adicionados à grade curricular!")

        if disciplina in self.grade_curricular:
            raise ValueError(f"ERRO: '{disciplina.nome}' já faz parte da grade de '{self.nome}'!")

        self.grade_curricular.append(disciplina)


    def calcular_carga_horaria_total(self) -> int:
        """Varre a grade curricular somando a carga horária de todos os cursos vinculados."""

        if not self.grade_curricular:
            raise ValueError(f"ERRO: '{self.nome}' não possui disciplinas cadastradas!")

        return sum(curso.carga_horaria for curso in self.grade_curricular)


    def verificar_elegibilidade_formatura(self, historico_aluno: "list[Matricula]") -> bool:
        """Compara o histórico do aluno com a grade curricular para determinar se ele pode colar grau."""

        if not self.grade_curricular:
            raise ValueError(f"ERRO: A graduação '{self.nome}' não possui disciplinas cadastradas na grade!")

        if not historico_aluno:
            raise ValueError("ERRO: O aluno não possui histórico de disciplinas cursadas!")

        # Extrai os nomes APENAS das disciplinas em que o aluno tem a situação 'Aprovado'.
        # O uso de Set {} elimina duplicidades automaticamente e ignora reprovações passadas.
        disciplinas_aprovadas = {
            matricula.turma.curso.nome
            for matricula in historico_aluno
            if matricula.status == "Aprovado"
        }

        # Varre a grade curricular da graduação.
        for disciplina in self.grade_curricular:

            # Se a disciplina exigida não estiver dentro do conjunto de disciplinas aprovadas do aluno, ele não forma.
            if disciplina.nome not in disciplinas_aprovadas:
                return False

        return True