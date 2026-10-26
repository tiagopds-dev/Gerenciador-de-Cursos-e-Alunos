import json
import re
from datetime import date
from pathlib import Path


class Configuracao:
    """
    Responsável por isolar as regras de negócio parametrizáveis. Lê dados de
    um arquivo (JSON) e centraliza parâmetros como notas mínimas e prazos de trancamento.
    """

    def __init__(self, caminho: str):

        caminho_arquivo = Path(caminho)

        if not caminho_arquivo.exists():
            raise ValueError("O caminho não existe!")

        if not caminho_arquivo.is_file():
            raise TypeError("O caminho não é um ficheiro!")

        # Delega integralmente o processo de leitura e validação para evitar duplicação de código
        self.carregar_configuracoes(caminho_arquivo)

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

        with open(caminho_arquivo, 'r') as arquivo:
            dados = json.load(arquivo)

        self._nota_minima_aprovacao = self.__validar_nota(dados['nota_minima_aprovacao'])
        self._frequencia_minima = self.__validar_frequencia(dados['frequencia_minima'])
        self._max_turmas_por_aluno = self.__validar_max_turmas(dados['max_turmas_por_aluno'])
        self._top_n_alunos = self.__validar_top_n(dados['top_n_alunos'])
        self._semestre_vigente = self.__validar_semestre(dados['semestre_vigente'])
        self._data_limite_trancamento = date.fromisoformat(dados['data_limite_trancamento'])


    # MÉTODOS PRIVADOS DE VALIDAÇÃO

    def __validar_nota(self, valor: float) -> float:

        if isinstance(valor, bool) or not isinstance(valor, (float, int)):
            raise TypeError("A nota mínima deve ser um valor numérico!")

        if valor < 0 or valor > 10:
            raise ValueError("A nota mínima deve estar entre 0 e 10!")

        return float(valor)

    def __validar_frequencia(self, valor: float) -> float:

        if isinstance(valor, bool) or not isinstance(valor, (float, int)):
            raise TypeError("A frequência mínima deve ser um valor numérico!")

        if valor < 0 or valor > 100:
            raise ValueError("A frequência mínima deve estar entre 0 e 100!")

        return float(valor)

    def __validar_max_turmas(self, valor: int) -> int:

        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("O limite de turmas deve ser um valor inteiro!")

        if valor <= 0 or valor > 10:
            raise ValueError("O limite máximo de turmas deve estar entre 1 e 10!")

        return valor

    def __validar_top_n(self, valor: int) -> int:

        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("O top N alunos deve ser um número inteiro!")

        if valor <= 0:
            raise ValueError("O valor de top N alunos deve ser maior que zero!")

        return valor

    def __validar_semestre(self, valor: str) -> str:

        if not isinstance(valor, str):
            raise TypeError("O semestre vigente deve estar em formato de texto!")

        # Valida o padrão exato de 4 dígitos seguidos de .1 ou .2
        if len(valor) != 6 or not re.match(r"^\d{4}\.[12]$", valor):
            raise ValueError(f"Formato de semestre inválido ('{valor}'). Utilize o padrão AAAA.S (ex: 2026.2).")

        return valor