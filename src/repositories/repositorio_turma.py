import json
from pathlib import Path
from src.domain.models.turmas import Turma
from src.domain.models.cursos import Curso


# Construção da classe.
class RepositorioTurma:
    """
    Responsável por isolar a lógica de persistência das turmas.
    Salva e restaura o estado global da classe (contador sequencial de IDs)
    e reconstrói as chaves estrangeiras que ligam a Turma ao seu respectivo Curso.
    """


    def __init__(self) -> None:

        # Define o caminho fixo do arquivo JSON responsável pelas turmas.
        self.__caminho_arquivo = Path("data/turmas.json")


    def salvar(self, turmas: list[Turma]) -> None:
        """
        Converte a lista de objetos Turma em um dicionário mestre JSON,
        armazenando também o contador global da classe para evitar reinicialização.
        """

        # Cria uma lista isolada para satisfazer o analisador estático de tipos.
        lista_dados = []

        for turma in turmas:

            # Extrai os dados da turma e armazena apenas o código do curso (chave estrangeira).
            lista_dados.append({
                "id_turma": turma.id_turma,
                "periodo": turma.periodo,
                "dias_horarios": turma.dias_horarios,
                "vagas": turma.vagas,
                "local": turma.local,
                "status": turma.status,
                "ativo": turma.ativo,
                "curso_codigo": turma.curso.codigo
            })

        # Estrutura o dicionário híbrido final: metadados da classe e a lista populada de objetos.
        turmas_exportacao = {
            "metadados": {
                "contador_turma": Turma._contador_turma
            },
            "dados": lista_dados
        }

        # Garante que a pasta 'data/' existe antes de tentar criar o arquivo.
        self.__caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        # Abre o arquivo em modo de escrita ('w') e injeta os dados convertidos.
        with open(self.__caminho_arquivo, "w", encoding="utf-8") as arquivo:

            # Salva o arquivo JSON com formatação amigável (identação) e aceitando caracteres especiais.
            json.dump(turmas_exportacao, arquivo, indent=4, ensure_ascii=False)


    def carregar(self, cursos_disponiveis: list[Curso]) -> list[Turma]:
        """
        Lê o arquivo JSON do disco, restaura o contador da classe,
        instancia as turmas e restabelece os vínculos bidirecionais com os Cursos.
        """

        # Se o arquivo não existir, é a primeira execução. Retorna uma lista vazia.
        if not self.__caminho_arquivo.exists():

            print("O caminho ('data/turmas.json') não foi encontrado! Retornando uma lista vazia.")

            return []

        # Prevenção caso o caminho exista, mas aponte para um diretório em vez de arquivo.
        if not self.__caminho_arquivo.is_file():

            print("O caminho ('data/turmas.json') não é um ficheiro válido! Retornando uma lista vazia.")

            return []

        turmas_reconstruidas = []

        # Abre o arquivo em modo de leitura ('r') e carrega o dicionário mestre.
        with open(self.__caminho_arquivo, "r", encoding="utf-8") as arquivo:

            dict_turmas_importacao = json.load(arquivo)

        # Reconstrói os objetos do domínio iterando sobre a chave 'dados' do JSON.
        for turma_dict in dict_turmas_importacao["dados"]:

            curso_encontrado = None

            # Varre os cursos já instanciados em busca da chave estrangeira correspondente.
            for curso in cursos_disponiveis:

                if curso.codigo == turma_dict["curso_codigo"]:

                    curso_encontrado = curso
                    break

            # Trava de segurança para satisfazer a tipagem estrita e proteger a integridade.
            if curso_encontrado is None:
                raise ValueError(
                    f"Corrupção de dados: O curso '{turma_dict['curso_codigo']}' "
                    f"não foi encontrado para recriar a turma '{turma_dict['id_turma']}'!"
                )

            # Instancia a turma original (o construtor da Turma já faz o vínculo com o curso internamente).
            nova_turma = Turma(
                turma_dict["periodo"],
                turma_dict["dias_horarios"],
                turma_dict["vagas"],
                turma_dict["local"],
                curso_encontrado
            )

            # Fura o encapsulamento de forma controlada para restaurar o ID exato, o status e a atividade.
            nova_turma._id_turma = turma_dict["id_turma"]

            nova_turma.status = turma_dict["status"]

            nova_turma.ativo = turma_dict.get("ativo", True)

            turmas_reconstruidas.append(nova_turma)

        # Sobrescreve o contador sequencial da classe com o valor real salvo nos metadados do JSON.
        Turma._contador_turma = dict_turmas_importacao["metadados"]["contador_turma"]

        return turmas_reconstruidas