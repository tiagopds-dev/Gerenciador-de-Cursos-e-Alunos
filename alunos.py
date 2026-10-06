from pessoas import Pessoa
from graduacoes import Graduacao
from datetime import date


class Aluno(Pessoa):
    """
    Especializa a classe Pessoa, adicionando uma matrícula única, o vínculo com a sua 
    Graduação e um histórico acadêmico. Responsável por calcular o Coeficiente de Rendimento (CR).
    """

    # Cria um atributo de classe para atua como contador sequencial
    # Pertence à classe Aluno, assim, não é resetado a cada novo objeto
    _contador_alunos = 1

    # Construção da classe
    def __init__(self, nome: str, cpf: str, telefone: str, email: str, graduacao: Graduacao) -> None:
        # Chama o construtor da classe Base (Pessoa) para validar e salvar os dados básicos
        super().__init__(nome, cpf, telefone, email)

        # Gera a matrícula automática utilizando um padrão pré-estabelecido (com base na UFCA)
        # (Ano atual + 00 + Identificador único do aluno)
        # :04d força o número a ter 4 casas, preenchendo com zeros à esquerda
        self._matricula = f"{date.today().year}00{Aluno._contador_alunos:04d}"

        # Incrementa o contador da classe para o próximo aluno que for criado
        Aluno._contador_alunos += 1

        # Inicializa o histórico como uma lista vazia (momento da criação)
        self._historico = []

        # Atribui a graduação como atributo vinculado diretamente a um aluno
        self.graduacao = graduacao


    # Como a matrícula será gerada sempre de forma automática, não será criado um setter
    # Dessa forma, não haverá como alterar a matrícula após a criação (apenas leitura)
    @property
    def matricula(self):
        return self._matricula

    # Permite leitura e modificações internas na lista (ex: .append), 
    # mas a ausência do Setter impede a substituição acidental de todo o histórico
    @property
    def historico(self):
        return self._historico


    # Usa o decorador para garantir que o Coeficiente não fique desatualizado, fique blindado contra edição
    # e tenha uma sitanxe de utilização limpa
    @property
    def cr(self) -> float:
        """Calcula o coeficiente de rendimento/média ponderada com base nas disciplinas do histórico."""

        # Caso o histórico esteja vazio (ex.: calouro) atribui diretamente 0.0 ao CR.
        if not self.historico:
            return 0.0

        # Utiliza uma expressão geradora para calcular a soma de todas as medias finais armazenadas
        # no histórico
        notas_somadas = sum(matricula.notas["media_final"] for matricula in self.historico)

        # Calcula o CR por meio de uma média aritmética entre as médias finais de cada turma
        # e a quantidade de turmas concluídas.
        media = notas_somadas/len(self.historico)

        # Retorna o valor arredondado para duas cadas decimais
        return round(media, 2)


    def __lt__(self, other):
        """
        Método especial que possibilita a comparação e, consequentemente, a ordenação de CRs.
        Base para o cálculo do ranking de alunos.
        """

        # Garante que a comparação seja feita entre dois objetos da classe Aluno
        if not isinstance(other, Aluno):
            return NotImplemented

        # Num primeiro momento, o cálculo será feito somente caso os dois CR sejam diferentes
        if self.cr != other.cr:
            return self.cr < other.cr

        # Caso os dois CRs sejam iguais, o nome será considerado critério de desempate
        return self.nome < other.nome