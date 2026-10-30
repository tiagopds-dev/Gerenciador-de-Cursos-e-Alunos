import json
from pathlib import Path
from src.domain.models.alunos import Aluno
from src.domain.models.turmas import Turma
from src.domain.models.matriculas import Matricula


# Construção da classe.
class RepositorioMatricula:
    """
    Responsável por isolar a lógica de persistência das matrículas.
    Reconstrói o elo (a ponte) entre Aluno e Turma a partir de múltiplas chaves estrangeiras.
    """

    def __init__(self) -> None:

        # Define o caminho fixo do arquivo JSON responsável pelas matrículas.
        self.__caminho_arquivo = Path("data/matriculas.json")

    def salvar(self, matriculas: list[Matricula]) -> None:
        """Converte a lista de objetos Matricula em formato JSON e escreve no disco."""

        matriculas_exportacao = []

        for matricula in matriculas:
            # Extrai apenas as chaves estrangeiras e o estado atual da matrícula.
            matriculas_exportacao.append({
                "aluno_matricula": matricula.aluno.matricula,
                "turma_id": matricula.turma.id_turma,
                "status": matricula.status
            })

        # Garante que a pasta 'data/' existe antes de tentar criar o arquivo.
        self.__caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        # Abre o arquivo em modo de escrita ('w') e injeta os dados convertidos.
        with open(self.__caminho_arquivo, "w", encoding="utf-8") as arquivo:
            # Salva o arquivo JSON com formatação amigável (identação) e aceitando caracteres especiais.
            json.dump(matriculas_exportacao, arquivo, indent=4, ensure_ascii=False)

    def carregar(self, alunos_disponiveis: list[Aluno], turmas_disponiveis: list[Turma]) -> list[Matricula]:
        """Lê o arquivo JSON e reconstrói as matrículas ligando os objetos Aluno e Turma."""

        # Se o arquivo não existir, é a primeira execução. Retorna uma lista vazia.
        if not self.__caminho_arquivo.exists():
            print("O caminho ('data/matriculas.json') não foi encontrado! Retornando uma lista vazia.")

            return []

        # Prevenção caso o caminho exista, mas aponte para um diretório em vez de arquivo.
        if not self.__caminho_arquivo.is_file():
            print("O caminho ('data/matriculas.json') não é um ficheiro válido! Retornando uma lista vazia.")

            return []

        matriculas_reconstruidas = []

        # Abre o arquivo em modo de leitura ('r') e carrega a lista de dicionários.
        with open(self.__caminho_arquivo, "r", encoding="utf-8") as arquivo:

            matriculas_importacao = json.load(arquivo)

        # Reconstrói os objetos iterando sobre os dados importados.
        for matricula_dict in matriculas_importacao:

            aluno_encontrado = turma_encontrada = None

            # Varre a lista de alunos para encontrar a chave estrangeira correspondente.
            for aluno in alunos_disponiveis:

                if aluno.matricula == matricula_dict["aluno_matricula"]:
                    aluno_encontrado = aluno
                    break

            # Varre a lista de turmas para encontrar a chave estrangeira correspondente.
            for turma in turmas_disponiveis:

                if turma.id_turma == matricula_dict["turma_id"]:
                    turma_encontrada = turma
                    break

            # Travas de segurança para satisfazer a tipagem estrita e proteger a integridade.
            if aluno_encontrado is None:
                raise ValueError(
                    f"Corrupção de dados: O aluno com matrícula '{matricula_dict['aluno_matricula']}' "
                    f"não foi encontrado para recriar a matrícula!"
                )

            if turma_encontrada is None:
                raise ValueError(
                    f"Corrupção de dados: A turma com ID '{matricula_dict['turma_id']}' "
                    f"não foi encontrada para recriar a matrícula do aluno '{matricula_dict['aluno_matricula']}'!"
                )

            # Instancia a matrícula (o construtor deve tratar os vínculos de histórico de forma automática).
            nova_matricula = Matricula(aluno_encontrado, turma_encontrada)

            # Restaura o status exato salvo no disco (ex: 'Ativa', 'Cancelada', etc.).
            nova_matricula.status = matricula_dict["status"]

            matriculas_reconstruidas.append(nova_matricula)

        return matriculas_reconstruidas