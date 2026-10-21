from pessoas import Pessoa
from datetime import date
from typing import TYPE_CHECKING

# Permite importar as classes estritamente para realizar o Type Hinting
# Resolve os alertas da IDE sem causar o erro fatal de importação circular em tempo real
if TYPE_CHECKING:
    from graduacoes import Graduacao


class Aluno(Pessoa):
    """
    Especializa a classe Pessoa, adicionando uma matrícula única, o vínculo com a sua
    Graduação e um histórico acadêmico. Responsável por calcular o Coeficiente de Rendimento (CR).
    """

    # Cria um atributo de classe que atua como contador sequencial
    # Pertence à classe Aluno, assim, não é reinicializado a cada novo objeto
    _contador_alunos = 1

    # Construção da classe
    def __init__(self, nome: str, cpf: str, telefone: str, email: str, graduacao: 'Graduacao') -> None:
        # Chama o construtor da classe Base (Pessoa) para validar e salvar os dados básicos
        super().__init__(nome, cpf, telefone, email)

        # Gera a matrícula automática utilizando um padrão pré-estabelecido (com base na UFCA)
        # (Ano atual + 00 + Identificador único do aluno)
        # ':04d' força o número a ter 4 casas, preenchendo com zeros à esquerda
        self._matricula = f"{date.today().year}00{Aluno._contador_alunos:04d}"

        # Incrementa o contador da classe para o próximo aluno que for criado
        Aluno._contador_alunos += 1

        # Inicializa o histórico como uma lista vazia (momento da criação)
        self._historico = []

        # Passa pelo setter para garantir que o objeto passado pertence à classe Graduacao
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


    @property
    def graduacao(self):
        return self._graduacao


    @graduacao.setter
    def graduacao(self, nova_graduacao: 'Graduacao'):

        # Verifica se o objeto passado realmente pertence à classe Graduacao
        # (Substitui o isinstance para evitar erro com o TYPE_CHECKING em execução real)
        if nova_graduacao.__class__.__name__ != 'Graduacao':
            raise TypeError("A graduação deve ser um objeto válido da classe Graduacao!")

        # Caso pertença, realiza a atribuição segura
        self._graduacao = nova_graduacao


    # Usa o decorador para garantir que o Coeficiente não fique desatualizado, fique blindado contra edição
    # e tenha uma sintaxe de utilização limpa
    @property
    def cr(self) -> float:
        """Calcula o coeficiente de rendimento/média ponderada com base nas disciplinas concluídas."""

        # Cria uma lista apenas com as matrículas do histórico que já foram concluídas (MF consolidada)
        turmas_concluidas = [matricula for matricula in self.historico if matricula.notas['MF'] is not None]

        # Caso o histórico de disciplinas concluídas esteja vazio (ex.: calouro), atribui diretamente 0.0
        if not turmas_concluidas:
            return 0.0

        # Cálculo da Média Ponderada: (Soma de Notas * Carga Horária) / Carga Horária Total Cursada
        soma_ponderada = sum(mat.notas['MF'] * mat.turma.curso.carga_horaria for mat in turmas_concluidas)
        carga_horaria_total = sum(mat.turma.curso.carga_horaria for mat in turmas_concluidas)

        # Medida de segurança contra divisão por zero
        if carga_horaria_total == 0:
            return 0.0

        # Calcula o CR dividindo a soma ponderada pelo total de horas cursadas
        cr = soma_ponderada / carga_horaria_total

        # Retorna o valor arredondado para duas casas decimais
        return round(cr, 2)


    # Adicionado Type Hinting na assinatura ('Aluno')
    def __lt__(self, other: 'Aluno'):
        """
        Método especial que possibilita a comparação e, consequentemente, a ordenação de CRs.
        Base para o cálculo do ranking de alunos.
        """

        # Garante que a comparação seja feita entre dois objetos da classe Aluno
        if other.__class__.__name__ != 'Aluno':
            return NotImplemented

        # Inicialmente, o cálculo será feito somente caso os dois CRs sejam diferentes
        if self.cr != other.cr:
            return self.cr < other.cr

        # Caso os dois CRs sejam iguais, a ordem alfabética do nome será considerada critério de desempate
        return self.nome < other.nome