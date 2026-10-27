import json
from pathlib import Path
from src.domain.models.graduacoes import Graduacao


# Construção da classe.
class RepositorioGraduacao:
    """
    Responsável por isolar a lógica de persistência das graduações.
    Lê e escreve os dados da memória em um arquivo JSON específico.
    """


    def __init__(self) -> None:

        # Define o caminho fixo do arquivo JSON responsável pelas graduações.
        self.__caminho_arquivo = Path("data/graduacoes.json")


    def salvar(self, graduacoes: list[Graduacao]) -> None:
        """Converte a lista de objetos Graduacao em formato JSON e escreve no disco."""

        graduacoes_exportacao = []

        # Extrai apenas as chaves primárias e atributos base de cada objeto.
        for graduacao in graduacoes:

            graduacoes_exportacao.append({
                "codigo_mec": graduacao.codigo_mec,
                "nome": graduacao.nome,
                "qtd_semestres": graduacao.qtd_semestres
            })

        # Garante que a pasta 'data/' existe antes de tentar criar o arquivo.
        self.__caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        # Abre o arquivo em modo de escrita ('w') e injeta os dados convertidos.
        with open(self.__caminho_arquivo, "w", encoding="utf-8") as arquivo:

            # Salva o arquivo JSON com formatação amigável (identação) e aceitando caracteres especiais.
            json.dump(graduacoes_exportacao, arquivo, indent=4, ensure_ascii=False)


    def carregar(self) -> list[Graduacao]:
        """Lê o arquivo JSON do disco e reconstrói as instâncias da classe Graduacao."""

        # Se o arquivo não existir, é a primeira execução. Retorna uma lista vazia.
        if not self.__caminho_arquivo.exists():

            print("O caminho ('data/graduacoes.json') não foi encontrado! Retornando uma lista vazia.")

            return []

        # Prevenção caso o caminho exista, mas aponte para um diretório em vez de arquivo.
        if not self.__caminho_arquivo.is_file():

            print("O caminho ('data/graduacoes.json') não é um ficheiro válido! Retornando uma lista vazia.")

            return []

        graduacoes_reconstruidas = []

        # Abre o arquivo em modo de leitura ('r') e carrega os dicionários.
        with open(self.__caminho_arquivo, "r", encoding="utf-8") as arquivo:

            graduacoes_importacao = json.load(arquivo)

        # Reconstrói os objetos do domínio utilizando os dados extraídos.
        for graduacao in graduacoes_importacao:

            nova_graduacao = Graduacao(
                graduacao["codigo_mec"],
                graduacao["nome"],
                graduacao["qtd_semestres"]
            )

            graduacoes_reconstruidas.append(nova_graduacao)

        return graduacoes_reconstruidas