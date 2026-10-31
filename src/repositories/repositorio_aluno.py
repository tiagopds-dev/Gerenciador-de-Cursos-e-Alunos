import json
from pathlib import Path
from src.domain.models.alunos import Aluno
from src.domain.models.graduacoes import Graduacao


# Construção da classe.
class RepositorioAluno:
    """
    Responsável por isolar a lógica de persistência dos alunos.
    Salva e restaura o estado global da classe (contador de matrícula)
    e reconstrói a chave estrangeira que liga o Aluno à sua Graduação.
    """


    def __init__(self) -> None:

        # Define o caminho fixo do arquivo JSON responsável pelos alunos.
        self.__caminho_arquivo = Path("data/alunos.json")


    def salvar(self, alunos: list[Aluno]) -> None:
        """
        Converte a lista de objetos Aluno em um dicionário mestre JSON,
        armazenando o contador global da classe e omitindo o histórico de matrículas.
        """

        # Cria uma lista isolada para satisfazer o analisador estático de tipos.
        lista_dados = []

        for aluno in alunos:

            # Extrai os dados do aluno e armazena apenas o código da graduação (chave estrangeira).
            lista_dados.append({
                "nome": aluno.nome,
                "cpf": aluno.cpf,
                "telefone": aluno.telefone,
                "email": aluno.email,
                "matricula": aluno.matricula,
                "ativo": aluno.ativo,
                "graduacao_codigo": aluno.graduacao.codigo_mec
            })

        # Estrutura o dicionário híbrido final: metadados da classe e a lista populada de objetos.
        alunos_exportacao = {
            "metadados": {
                "contador_aluno": Aluno._contador_alunos
            },
            "dados": lista_dados
        }

        # Garante que a pasta 'data/' existe antes de tentar criar o arquivo.
        self.__caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        # Abre o arquivo em modo de escrita ('w') e injeta os dados convertidos.
        with open(self.__caminho_arquivo, "w", encoding="utf-8") as arquivo:

            # Salva o arquivo JSON com formatação amigável (identação) e aceitando caracteres especiais.
            json.dump(alunos_exportacao, arquivo, indent=4, ensure_ascii=False)


    def carregar(self, graduacoes_disponiveis: list[Graduacao]) -> list[Aluno]:
        """
        Lê o arquivo JSON do disco, restaura o contador da classe,
        instancia os alunos e restabelece os vínculos com as Graduações.
        """

        # Se o arquivo não existir, é a primeira execução. Retorna uma lista vazia.
        if not self.__caminho_arquivo.exists():

            print("O caminho ('data/alunos.json') não foi encontrado! Retornando uma lista vazia.")

            return []

        # Prevenção caso o caminho exista, mas aponte para um diretório em vez de arquivo.
        if not self.__caminho_arquivo.is_file():

            print("O caminho ('data/alunos.json') não é um ficheiro válido! Retornando uma lista vazia.")

            return []

        alunos_reconstruidos = []

        # Abre o arquivo em modo de leitura ('r') e carrega o dicionário mestre.
        with open(self.__caminho_arquivo, "r", encoding="utf-8") as arquivo:

            dict_alunos_importacao = json.load(arquivo)

        # Reconstrói os objetos do domínio iterando sobre a chave 'dados' do JSON.
        for aluno_dict in dict_alunos_importacao["dados"]:

            graduacao_encontrada = None

            # Varre as graduações já instanciadas em busca da chave estrangeira correspondente.
            for graduacao in graduacoes_disponiveis:

                if graduacao.codigo_mec == aluno_dict["graduacao_codigo"]:

                    graduacao_encontrada = graduacao
                    break

            # Trava de segurança para satisfazer a tipagem estrita e proteger a integridade dos dados.
            if graduacao_encontrada is None:
                raise ValueError(
                    f"Corrupção de dados: A graduação '{aluno_dict['graduacao_codigo']}' "
                    f"não foi encontrada para recriar o aluno '{aluno_dict['nome']}'!"
                )

            # Instancia o aluno original (o construtor de Aluno já faz o vínculo com a Graduacao internamente).
            novo_aluno = Aluno(
                aluno_dict["nome"],
                aluno_dict["cpf"],
                aluno_dict["telefone"],
                aluno_dict["email"],
                graduacao_encontrada
            )

            # Fura o encapsulamento de forma controlada para restaurar a matrícula exata e o status de atividade.
            novo_aluno._matricula = aluno_dict["matricula"]

            novo_aluno.ativo = aluno_dict.get("ativo", True)

            alunos_reconstruidos.append(novo_aluno)

        # Sobrescreve o contador sequencial da classe com o valor real salvo nos metadados do JSON.
        Aluno._contador_alunos = dict_alunos_importacao["metadados"]["contador_aluno"]

        return alunos_reconstruidos