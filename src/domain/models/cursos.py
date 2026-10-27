import re
from typing import TYPE_CHECKING

# Permite importar as classes estritamente para realizar o Type Hinting.
# Resolve os alertas da IDE sem causar o erro fatal de importação circular em tempo real.
if TYPE_CHECKING:
    from src.domain.models.turmas import Turma
    from src.domain.models.graduacoes import Graduacao


# Construção da classe.
class Curso:
    """
    Representa a disciplina na sua essência. Guarda a ementa, carga horária
    e a lista de pré-requisitos necessários para ser cursada.
    """


    def __init__(self, nome: str, carga_horaria: int, pre_requisitos: list, ementa: str, graduacao: "Graduacao") -> None:

        # Validação e associação da dependência principal (Graduação).
        if graduacao.__class__.__name__ != "Graduacao":
            raise TypeError("A graduação vinculada deve ser um objeto válido da classe 'Graduacao'!")

        self.graduacao = graduacao

        # Geração automática do código do curso.
        # Captura a primeira letra de cada palavra (maior que 3 letras) do nome da graduação e converte para maiúscula.
        iniciais_graduacao = "".join(palavra[0].upper() for palavra in self.graduacao.nome.split() if len(palavra) > 3)

        # Gera o identificador: Sigla + Número do próximo curso na grade (preenchido com zeros).
        self._codigo = f"{iniciais_graduacao}{(len(self.graduacao.grade_curricular) + 1):04d}"

        # Inicialização dos dados base (acionando as validações dos setters).
        self.nome = nome

        self.carga_horaria = carga_horaria

        self.ementa = ementa

        # Validação e inicialização de pré-requisitos.
        if not isinstance(pre_requisitos, list):
            raise TypeError("Os pré-requisitos do curso devem ser fornecidos em formato de lista (mesmo que vazia)!")

        # Inicializa como protegido, permitindo leitura, mas impedindo a sobrescrita total por engano.
        self._pre_requisitos = pre_requisitos

        # O histórico de turmas ofertadas nasce como uma lista vazia no momento da criação do curso.
        self._turmas_ofertadas = []


    @property
    def nome(self):
        return self._nome


    @nome.setter
    def nome(self, novo_nome: str):

        if not isinstance(novo_nome, str):
            raise TypeError("O nome do curso deve ser enviado em formato de texto!")

        # Retira caracteres inválidos e converte tudo em minúsculas para a base de formatação.
        novo_nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", novo_nome).lower()

        if not novo_nome.strip() or len(novo_nome) < 6:
            raise ValueError("O nome do curso deve conter pelo menos 6 letras válidas!")

        # Lista de exceções para não capitalizar artigos e preposições.
        excecoes = {"de", "da", "do", "das", "dos", "a", "e", "o", "as", "os", "em", "por", "para", "com"}

        # Formatação inteligente usando List Comprehension.
        # Capitaliza a primeira palavra (índice 0) OU se a palavra NÃO estiver nas exceções.
        palavras = [
            p.capitalize() if i == 0 or p not in excecoes else p
            for i, p in enumerate(novo_nome.split())
        ]

        # Segue com a atribuição final da string polida.
        self._nome = " ".join(palavras)


    # Como o código do curso será gerado sempre de forma automática, não será criado um setter.
    # Dessa forma, não haverá como alterar o código do curso após a criação (apenas leitura).
    @property
    def codigo(self):
        return self._codigo


    @property
    def carga_horaria(self):
        return self._carga_horaria


    @carga_horaria.setter
    def carga_horaria(self, nova_carga_horaria: int):

        # Verifica se o tipo de dado passado foi correto (blindagem contra booleanos e textos).
        if isinstance(nova_carga_horaria, bool) or not isinstance(nova_carga_horaria, int):
            raise TypeError("A carga horária do curso deve ser informada exclusivamente como um número inteiro!")

        # Impede a atualização da carga horária caso o valor passado seja zero ou negativo.
        if nova_carga_horaria <= 0:
            raise ValueError(f"A carga horária deve ser estritamente positiva! Valor recebido: {nova_carga_horaria}h.")

        self._carga_horaria = nova_carga_horaria


    # Permite leitura e modificações internas na lista de pré-requisitos (ex: '.append'),
    # mas a ausência do Setter impede a substituição acidental de todos os pré-requisitos.
    @property
    def pre_requisitos(self):
        return self._pre_requisitos


    @property
    def ementa(self):
        return self._ementa


    @ementa.setter
    def ementa(self, nova_ementa: str):

        if not isinstance(nova_ementa, str):
            raise TypeError("A ementa do curso deve ser enviada em formato de texto!")

        # Remove espaços em branco desnecessários nas extremidades.
        nova_ementa = nova_ementa.strip()

        if not nova_ementa or len(nova_ementa) < 100:
            raise ValueError(
                f"Ementa muito curta (Atual: {len(nova_ementa)} caracteres)! "
                f"É exigido um mínimo de 100 caracteres detalhando a disciplina."
            )

        self._ementa = nova_ementa


    # Permite a leitura e modificações internas na lista que armazena o histórico de turmas ofertadas,
    # mas a ausência do Setter impede a exclusão acidental do histórico.
    @property
    def turmas_ofertadas(self):
        return self._turmas_ofertadas


    def alterar_carga_horaria(self, nova_carga_horaria: int, nova_ementa: str) -> None:
        """
        Atualiza a estrutura base da disciplina (ementa e horas).
        Bloqueia a modificação automaticamente caso o curso possua turmas em andamento.
        """

        if not isinstance(nova_ementa, str):
            raise TypeError("A nova ementa deve ser enviada em formato de texto!")

        if isinstance(nova_carga_horaria, bool) or not isinstance(nova_carga_horaria, int):
            raise TypeError("A nova carga horária deve ser informada como número inteiro!")

        # Verifica utilizando o gerador any() se há alguma turma cuja situação seja 'Aberta'.
        if any(turma.status == "Aberta" for turma in self.turmas_ofertadas):
            raise ValueError(
                f"Operação negada! Não é possível alterar a base do curso '{self.nome}' enquanto há turmas ativas."
            )

        # Reutiliza os próprios setters da classe para garantir que as novas validações de tamanho/formato se aplicam.
        self.ementa = nova_ementa

        self.carga_horaria = nova_carga_horaria


    def verificar_ciclo_dependencia(self, novo_pre_requisito: "Curso") -> None:
        """Impede dependências cruzadas (ex: A exige B e B exige A simultaneamente) para evitar paradoxos na grade."""

        # Validação estrita de tipo usando o nome da classe.
        if novo_pre_requisito.__class__.__name__ != "Curso":
            raise TypeError("O pré-requisito deve ser um objeto válido da classe 'Curso'!")

        # Inspeciona a lista de exigências do curso que está a tentar ser adicionado.
        # Se o curso atual já estiver lá, uma adição mútua criaria um paradoxo.
        if self in novo_pre_requisito.pre_requisitos:
            raise ValueError(
                f"ERRO: Ciclo de dependência detectado! Não é possível adicionar '{novo_pre_requisito.nome}' "
                f"como pré-requisito, pois ele já exige '{self.nome}'."
            )

        # Caso não haja conflito estrutural, o curso é aprovado e anexado à lista.
        self.pre_requisitos.append(novo_pre_requisito)


    def vincular_turma(self, turma: "Turma") -> None:
        """
        Aplica o princípio do encapsulamento.
        Permite que uma Turma se registe no histórico deste Curso de forma segura,
        sem que seja necessário expor ou aceder ao atributo protegido '_turmas_ofertadas' diretamente.
        """

        if turma.__class__.__name__ != "Turma":
            raise TypeError("Apenas objetos da classe 'Turma' podem ser vinculados ao curso!")

        self._turmas_ofertadas.append(turma)


    def __str__(self) -> str:
        """Retorna uma representação amigável e formatada do curso por meio de uma string."""

        return f"Graduação: {self.graduacao.nome}\n{self.nome}\n{self.carga_horaria}h\nPré-requisitos: {self.pre_requisitos}"