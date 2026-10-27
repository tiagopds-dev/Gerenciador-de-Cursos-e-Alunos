import json
import re
from datetime import date
from pathlib import Path


# Construção da classe.
class Configuracao:
    """
    Responsável por isolar as regras de negócio parametrizáveis. Lê dados de
    um arquivo (JSON) e centraliza parâmetros como notas mínimas e prazos de trancamento.
    """


    def __init__(self, caminho: str) -> None:

        # Converte a string recebida em um objeto de caminho manipulável.
        caminho_arquivo = Path(caminho)

        # Verifica se o endereço informado realmente existe no sistema de arquivos.
        if not caminho_arquivo.exists():
            raise ValueError(f"O caminho informado ('{caminho}') não existe!")

        # Garante que o endereço aponta para um arquivo e não para um diretório.
        if not caminho_arquivo.is_file():
            raise TypeError(f"O caminho informado ('{caminho}') não é um ficheiro válido!")

        # Delega integralmente o processo de leitura e validação para evitar duplicação de código.
        self.carregar_configuracoes(caminho_arquivo)


    # Propriedades configuradas apenas para leitura (Read-Only), protegendo as regras de negócio.
    @property
    def nota_minima_aprovacao(self):
        return self._nota_minima_aprovacao


    @property
    def frequencia_minima(self):
        return self._frequencia_minima


    @property
    def data_limite_trancamento(self):
        return self._data_limite_trancamento


    @property
    def max_turmas_por_aluno(self):
        return self._max_turmas_por_aluno


    @property
    def top_n_alunos(self):
        return self._top_n_alunos


    @property
    def semestre_vigente(self):
        return self._semestre_vigente


    def carregar_configuracoes(self, caminho_arquivo: Path) -> None:
        """Lê os dados do arquivo JSON de configuração e atualiza os atributos da classe."""

        # Abre o arquivo em modo de leitura e carrega a estrutura JSON em um dicionário.
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:

            dados = json.load(arquivo)

        # Valida e atribui a nota mínima exigida para aprovação.
        self._nota_minima_aprovacao = self.__validar_nota(dados["nota_minima_aprovacao"])

        # Valida e atribui o percentual mínimo de frequência exigido.
        self._frequencia_minima = self.__validar_frequencia(dados["frequencia_minima"])

        # Valida e atribui o limite máximo de disciplinas simultâneas por aluno.
        self._max_turmas_por_aluno = self.__validar_max_turmas(dados["max_turmas_por_aluno"])

        # Valida e atribui a quantidade de alunos exibidos no ranking de melhores CRs.
        self._top_n_alunos = self.__validar_top_n(dados["top_n_alunos"])

        # Valida e atribui o semestre letivo atual da instituição.
        self._semestre_vigente = self.__validar_semestre(dados["semestre_vigente"])

        # Valida o tipo textual da data antes de realizar a conversão para objeto date.
        if not isinstance(dados["data_limite_trancamento"], str):
            raise TypeError("A data limite de trancamento deve ser enviada em formato de texto ('YYYY-MM-DD')!")

        # Converte a string no padrão ISO ('YYYY-MM-DD') em um objeto de data real do Python.
        self._data_limite_trancamento = date.fromisoformat(dados["data_limite_trancamento"])


    # Métodos privados de validação (protegidos com Name Mangling).
    def __validar_nota(self, valor: float) -> float:
        """Garante que a nota mínima seja numérica e esteja dentro da escala de 0 a 10."""

        # Impede valores booleanos ou tipos não numéricos.
        if isinstance(valor, bool) or not isinstance(valor, (float, int)):
            raise TypeError("A nota mínima de aprovação deve ser um valor numérico!")

        # Verifica se a nota respeita os limites matemáticos do sistema acadêmico.
        if valor < 0 or valor > 10:
            raise ValueError(f"A nota mínima deve estar entre 0 e 10! Você informou '{valor}'.")

        return float(valor)


    def __validar_frequencia(self, valor: float) -> float:
        """Garante que a frequência mínima seja numérica e represente uma porcentagem entre 0 e 100."""

        # Impede valores booleanos ou tipos não numéricos.
        if isinstance(valor, bool) or not isinstance(valor, (float, int)):
            raise TypeError("A frequência mínima deve ser um valor numérico!")

        # Verifica se o percentual está dentro do intervalo válido de 0% a 100%.
        if valor < 0 or valor > 100:
            raise ValueError(f"A frequência mínima deve estar entre 0 e 100! Você informou '{valor}'.")

        return float(valor)


    def __validar_max_turmas(self, valor: int) -> int:
        """Garante que o limite máximo de turmas por aluno seja um inteiro positivo plausível."""

        # Exige estritamente um número inteiro, barrando floats e booleanos.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("O limite máximo de turmas por aluno deve ser um número inteiro!")

        # Verifica se a quantidade de turmas simultâneas está dentro da faixa permitida.
        if valor <= 0 or valor > 10:
            raise ValueError(f"O limite máximo de turmas deve estar entre 1 e 10! Você informou '{valor}'.")

        return valor


    def __validar_top_n(self, valor: int) -> int:
        """Garante que o parâmetro de ranking Top N seja um número inteiro estritamente positivo."""

        # Exige estritamente um número inteiro, barrando floats e booleanos.
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("O parâmetro 'top_n_alunos' deve ser um número inteiro!")

        # Impede rankings vazios ou negativos.
        if valor <= 0:
            raise ValueError(f"O valor de 'top_n_alunos' deve ser maior que zero! Você informou '{valor}'.")

        return valor


    def __validar_semestre(self, valor: str) -> str:
        """Garante que o semestre vigente obedeça ao padrão 'AAAA.1' ou 'AAAA.2'."""

        # Verifica se o dado recebido é uma string.
        if not isinstance(valor, str):
            raise TypeError("O semestre vigente deve estar em formato de texto!")

        # Valida o padrão exato de 4 dígitos seguidos de '.1' ou '.2'.
        if len(valor) != 6 or not re.match(r"^\d{4}\.[12]$", valor):
            raise ValueError(f"Formato de semestre inválido ('{valor}')! Utilize o padrão 'AAAA.S' (ex: '2026.2').")

        return valor