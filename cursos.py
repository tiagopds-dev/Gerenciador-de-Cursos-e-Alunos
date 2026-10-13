from graduacoes import Graduacao
import re


class Curso:
    """
    Representa a disciplina na sua essência. Guarda a ementa, carga horária 
    e a lista de pré-requisitos necessários para ser cursada.
    """
    
    def __init__(self, nome: str, carga_horaria: int, pre_requisitos: list, ementa: str, graduacao: Graduacao) -> None:

        # Recebe um objeto do tipo Graduacao para realizar a associação
        self.graduacao = graduacao

        # Captura as iniciais da graduação (ignora preposições e artigos curtos) na construção do código do curso
        iniciais_graduacao = "".join(palavra[0] for palavra in self.graduacao.nome.split() if len(palavra) > 3)

        # Gera um código de curso automático utilizando um padrão pré-estabelecido
        # (Sigla da graduação + Identificador único do curso)
        # :04d força o número a ter 4 casas, preenchendo com zeros à esquerda
        self._codigo = f"{iniciais_graduacao}{len(self.graduacao.grade_curricular):04d}"

        # Inicializa o nome do curso (passando pela validação do setter)
        self.nome = nome

        # Inicializa a carga horária do curso (passando pela validação do setter)
        self.carga_horaria = carga_horaria

        # Inicializa os pré-requisitos como um atributo protegido, permitindo leitura, mas impedindo sobrescrita total acidental
        self._pre_requisitos = pre_requisitos

        # Inicializa a ementa do curso (passando pela validação do setter)
        self.ementa = ementa

        # Inicializa o histórico de turmas ofertadas para o curso como uma lista vazia (momento da criação)
        self._turmas_ofertadas = []


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def nome(self):
        return self._nome

    
    # Transforma a atribuição num Setter com validação obrigatória
    @nome.setter
    def nome(self, novo_nome):

        # Valida tamanho exato do argumento passado para nome e garante que seja uma string
        if not isinstance(novo_nome, str) or not novo_nome or len(novo_nome) < 6:
            raise Exception("Nome inválido!")

        # Retira quaisquer coisas que não sejam letras de A a Z, letras acentuadas (do À ao ÿ) e espaços
        # Formata o nome, deixando a primeira letra de cada palavra maiúscula
        novo_nome = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', novo_nome).title()

        # Segue com a atribuição se todas as verificações foram atendidas
        self._nome = novo_nome 

    
    # Como o código do curso será gerado sempre de forma automática, não será criado um setter
    # Dessa forma, não haverá como alterar o código do curso após a criação (apenas leitura)
    @property
    def codigo(self):
        return self._codigo


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def carga_horaria(self):
        return self._carga_horaria

    
    # Transforma a atribuição num Setter com validação obrigatória
    @carga_horaria.setter
    def carga_horaria(self, nova_carga_horaria: int):
        
        # Verifica se o tipo de dado passado no parâmetro do método foi correto (blindagem contra booleano)
        if isinstance(nova_carga_horaria, bool) or not isinstance(nova_carga_horaria, int):
            raise TypeError
        
        # Impede a atualização da carga horária caso o valor passado seja zero ou negativo
        if nova_carga_horaria <= 0:
            raise Exception("A carga horária do curso não pode ser menor ou igual a zero!")

        # Segue com a atribuição se todas as verificações foram atendidas
        self._carga_horaria = nova_carga_horaria


    # Permite leitura e modificações internas na lista de pré-requisitos (ex: .append), 
    # mas a ausência do Setter impede a substituição acidental de todo os pré-requisitos
    @property
    def pre_requisitos(self):
        return self._pre_requisitos

    
    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def ementa(self):
        return self._ementa

    
    # Transforma a atribuição num Setter com validação obrigatória
    @ementa.setter
    def ementa(self, nova_ementa):

        # Valida tamanho exato do argumento passado para a ementa e garante que seja string
        if not isinstance(nova_ementa, str) or not nova_ementa or len(nova_ementa) < 100:
            raise Exception("Ementa inválida. Ementa não pode estar vazia ou ser menor que 100 caracteres!")

        # Segue com a atribuição se todas as verificações foram atendidas
        self._ementa = nova_ementa

    # Permite a leitura e modificações internas na lista que armazena o histórico de turmas ofertadas (ex: .append), 
    # mas a ausência do Setter impede a substituição acidental do histórico
    @property
    def turmas_ofertadas(self):
        return self._turmas_ofertadas

    
    def alterar_carga_horaria(self, nova_carga_horaria: int, nova_ementa: str):
        """
        
        """
        
        # Verifica se o tipo de dado passado nos parâmetros do método foi correto (blindagem contra booleano e tipos errados)
        if not isinstance(nova_ementa, str) or isinstance(nova_carga_horaria, bool) or not isinstance(nova_carga_horaria, int):
            raise TypeError

        # Impede a alteração estrutural do curso caso exista alguma turma ativa vinculada a ele
        if "Aberta" in [turma.status for turma in self.turmas_ofertadas]:
            raise Exception("Não é possível alterar a ementa/carga horária de um curso enquanto há turmas ativas!")

        # Atualiza os atributos após validar os novos parâmetros
        self.ementa = nova_ementa
        self.carga_horaria = nova_carga_horaria


    def __str__(self) -> str:
        # Retorna uma representação amigável e formatada do curso por meio de uma string
        return f"Graduação: {self.graduacao.nome}\n{self.nome}\n{self.carga_horaria}h\nPré-requisitos: {self.pre_requisitos}"


    def verificar_ciclo_dependencia(self, novo_pre_requisito: str) -> bool:
        """Impede dependências cruzadas (ex: A exige B e B exige A simultaneamente)."""
        pass