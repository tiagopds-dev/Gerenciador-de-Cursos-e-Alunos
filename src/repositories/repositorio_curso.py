import json
from pathlib import Path
from src.domain.models.cursos import Curso
from src.domain.models.graduacoes import Graduacao


# Construção da classe.
class RepositorioCurso:
    """
    Responsável por isolar a lógica de persistência dos cursos.
    Aplica a hidratação em duas passagens (Two-Pass Hydration) para reconstruir
    os vínculos de graduação e a árvore de dependência dos pré-requisitos.
    """


    def __init__(self) -> None:

        # Define o caminho fixo do arquivo JSON responsável pelos cursos.
        self.__caminho_arquivo = Path("data/cursos.json")


    def salvar(self, cursos: list[Curso]) -> None:
        """Converte a lista de objetos Curso em formato JSON e escreve no disco."""

        cursos_exportacao = []

        for curso in cursos:

            # Extrai os dados base e converte as relações complexas em Chaves Estrangeiras (textos/códigos).
            cursos_exportacao.append({
                "codigo": curso.codigo,
                "nome": curso.nome,
                "carga_horaria": curso.carga_horaria,
                "ementa": curso.ementa,
                "ativo": curso.ativo,
                "graduacao_codigo": curso.graduacao.codigo_mec,
                "pre_requisitos_codigos": [pre_requisito.codigo for pre_requisito in curso.pre_requisitos]
            })

        # Garante que a pasta 'data/' existe antes de tentar criar o arquivo.
        self.__caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        # Abre o arquivo em modo de escrita ('w') e injeta os dados convertidos.
        with open(self.__caminho_arquivo, "w", encoding="utf-8") as arquivo:

            # Salva o arquivo JSON com formatação amigável (identação) e aceitando caracteres especiais.
            json.dump(cursos_exportacao, arquivo, indent=4, ensure_ascii=False)


    def carregar(self, graduacoes_disponiveis: list[Graduacao]) -> list[Curso]:
        """Lê o arquivo JSON, instancia os cursos e reconstrói as relações de pré-requisitos."""

        # Se o arquivo não existir, é a primeira execução. Retorna uma lista vazia.
        if not self.__caminho_arquivo.exists():

            print("O caminho ('data/cursos.json') não foi encontrado! Retornando uma lista vazia.")

            return []

        # Prevenção caso o caminho exista, mas aponte para um diretório em vez de arquivo.
        if not self.__caminho_arquivo.is_file():

            print("O caminho ('data/cursos.json') não é um ficheiro válido! Retornando uma lista vazia.")

            return []

        cursos_reconstruidos = []

        # Abre o arquivo em modo de leitura ('r') e carrega os dicionários.
        with open(self.__caminho_arquivo, "r", encoding="utf-8") as arquivo:

            cursos_importacao = json.load(arquivo)

        # Passagem 1: Criação básica dos objetos e vínculo com a Graduação.
        for curso_dict in cursos_importacao:

            graduacao_encontrada = None

            # Varre as graduações já instanciadas em busca da chave estrangeira correspondente.
            for graduacao in graduacoes_disponiveis:

                if graduacao.codigo_mec == curso_dict["graduacao_codigo"]:

                    graduacao_encontrada = graduacao
                    break

            # Trava de segurança para satisfazer a tipagem estrita e proteger a integridade dos dados.
            if graduacao_encontrada is None:
                raise ValueError(
                    f"Corrupção de dados: A graduação '{curso_dict['graduacao_codigo']}' "
                    f"não foi encontrada para recriar o curso '{curso_dict['nome']}'!"
                )

            # Instancia o curso passando uma lista de pré-requisitos vazia nesta primeira passagem.
            novo_curso = Curso(
                curso_dict["nome"],
                curso_dict["carga_horaria"],
                [],
                curso_dict["ementa"],
                graduacao_encontrada
            )

            # Restaura o código original e o status de Soft Delete guardados no disco.
            if "codigo" in curso_dict:
                novo_curso._codigo = curso_dict["codigo"]

            novo_curso.ativo = curso_dict.get("ativo", True)

            # Restabelece o vínculo bidirecional diretamente na grade para suportar graduações inativadas.
            graduacao_encontrada.grade_curricular.append(novo_curso)

            cursos_reconstruidos.append(novo_curso)

        # Passagem 2: Hidratação da árvore de pré-requisitos (associação Curso com Curso).
        # A função zip emparelha o dicionário (que tem os códigos) com o objeto recém-criado na memória.
        for curso_dict, curso_obj in zip(cursos_importacao, cursos_reconstruidos):

            for codigo_prereq in curso_dict["pre_requisitos_codigos"]:

                # Busca qual objeto Curso da memória corresponde ao código listado como pré-requisito.
                for curso_candidato in cursos_reconstruidos:

                    if curso_candidato.codigo == codigo_prereq:

                        # Adiciona o objeto Curso na lista do curso dependente.
                        curso_obj.pre_requisitos.append(curso_candidato)
                        break

        return cursos_reconstruidos