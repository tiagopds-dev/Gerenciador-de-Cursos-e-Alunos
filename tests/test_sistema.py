import json
from datetime import date, timedelta
from pathlib import Path
import pytest

from src.config.config import Configuracao
from src.domain.models.alunos import Aluno
from src.domain.models.turmas import Turma
from src.services.sistema import Sistema


# Massa de Dados Auxiliar e Fixtures de Isolamento

# Lista de CPFs matematicamente válidos (dígitos verificadores reais) para os testes.
CPFS_VALIDOS = [
    "52998224725",
    "11144477735",
    "12345678909",
    "39053344705",
    "71428793860",
    "28625587887",
    "98765432100"
]

EMENTA_PADRAO = (
    "Estudo aprofundado dos conceitos fundamentais da disciplina, abordando lógica formal, "
    "modelagem estruturada, abstração de dados, práticas de laboratório e projetos aplicados."
)

EMENTA_ATUALIZADA = (
    "Ementa reformulada contemplando arquiteturas modernas de software, padrões de projeto, "
    "testes automatizados, refatoração contínua, persistência de dados e boas práticas em POO."
)


@pytest.fixture
def sistema_limpo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Sistema:
    """
    Cria um ambiente temporário isolado (tmp_path) para cada teste, evitando que os
    ficheiros JSON reais da pasta 'data/' do projeto sejam modificados ou corrompidos.
    """

    # Redireciona o diretório de trabalho atual para a pasta temporária do pytest.
    monkeypatch.chdir(tmp_path)

    # Reinicializa os contadores sequenciais das classes de domínio para garantir determinismo.
    Aluno._contador_alunos = 1
    Turma._contador_turma = 1

    # Cria o diretório 'data/' e o ficheiro 'settings.json' de teste.
    pasta_data = tmp_path / "data"
    pasta_data.mkdir(parents=True, exist_ok=True)

    ano_atual = date.today().year
    data_limite = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")

    settings_teste = {
        "nota_minima_aprovacao": 7.0,
        "frequencia_minima": 75.0,
        "data_limite_trancamento": data_limite,
        "max_turmas_por_aluno": 3,
        "top_n_alunos": 2,
        "semestre_vigente": f"{ano_atual}.2"
    }

    caminho_settings = pasta_data / "settings.json"
    with open(caminho_settings, "w", encoding="utf-8") as arquivo:
        json.dump(settings_teste, arquivo, indent=4, ensure_ascii=False)

    config = Configuracao(str(caminho_settings))
    return Sistema(config)


# Testes de Domínio, Cadastros e Validações Estruturais

def test_01_cadastro_graduacao_curso_e_vinculo_grade(sistema_limpo: Sistema) -> None:
    """Verifica o cadastro de graduação e curso, geração de código único e o __str__."""

    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.buscar_graduacao("12345678")

    assert grad is not None
    assert grad.nome == "Engenharia de Software"

    sistema_limpo.cadastrar_curso("Algoritmos e Programação", 60, [], EMENTA_PADRAO, grad)
    curso = sistema_limpo.buscar_curso("ES0001")

    assert curso is not None
    assert curso.codigo == "ES0001"
    assert curso in grad.grade_curricular
    assert grad.calcular_carga_horaria_total() == 60
    assert "Algoritmos e Programação" in str(curso)


def test_02_impedir_ciclo_dependencia_pre_requisitos(sistema_limpo: Sistema) -> None:
    """Garante que o domínio bloqueia dependências circulares diretas (A exige B e B exige A)."""

    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Programação Estruturada", 60, [], EMENTA_PADRAO, grad)
    curso_a = sistema_limpo.cursos[0]

    sistema_limpo.cadastrar_curso("Estrutura de Dados", 60, [curso_a], EMENTA_PADRAO, grad)
    curso_b = sistema_limpo.cursos[1]

    # Tentar adicionar o Curso B como pré-requisito do Curso A deve levantar ValueError.
    with pytest.raises(ValueError, match="Ciclo de dependência"):
        curso_a.verificar_ciclo_dependencia(curso_b)


def test_03_validacao_cpf_invalido_e_duplicidade_aluno(sistema_limpo: Sistema) -> None:
    """Testa a rejeição de CPFs matematicamente inválidos e impede CPFs duplicados."""

    sistema_limpo.cadastrar_graduacao("12345678", "Ciência da Computação", 8)
    grad = sistema_limpo.graduacoes[0]

    # CPF com todos os dígitos iguais deve ser rejeitado.
    with pytest.raises(ValueError):
        sistema_limpo.cadastrar_aluno("João Silva", "11111111111", "88999990001", "joao@ufca.edu.br", grad)

    # CPF com dígitos verificadores incorretos deve ser rejeitado.
    with pytest.raises(ValueError):
        sistema_limpo.cadastrar_aluno("João Silva", "52998224700", "88999990001", "joao@ufca.edu.br", grad)

    # Cadastro válido seguido de tentativa de duplicidade do mesmo CPF.
    sistema_limpo.cadastrar_aluno("Maria Oliveira", CPFS_VALIDOS[0], "88999990001", "maria@ufca.edu.br", grad)

    with pytest.raises(ValueError, match="Já existe um aluno cadastrado"):
        sistema_limpo.cadastrar_aluno("Outro Aluno", CPFS_VALIDOS[0], "88999990002", "outro@ufca.edu.br", grad)


# Testes de Regras de Matrícula (Pré-requisitos, Choque, Vagas e Limites)

def test_04_matricula_sucesso_e_vinculo_historico(sistema_limpo: Sistema) -> None:
    """Testa a realização de matrícula válida e o vínculo bidirecional entre Aluno e Turma."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Banco de Dados", 60, [], EMENTA_PADRAO, grad)
    curso = sistema_limpo.cursos[0]

    sistema_limpo.abrir_turma(f"{ano}.2", {"seg": "08:00-10:00"}, 20, "Sala 101", curso)
    turma = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Tiago Pereira", CPFS_VALIDOS[0], "88999990001", "tiago@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    sistema_limpo.realizar_matricula(aluno, turma)

    assert len(turma) == 1
    assert len(aluno.historico) == 1
    assert aluno.historico[0] == turma.matriculas_ativas[0]
    assert aluno.historico[0].status == "Cursando"


def test_05_matricula_negada_pre_requisito_nao_atendido(sistema_limpo: Sistema) -> None:
    """Garante que a matrícula é negada caso o aluno não tenha cumprido os pré-requisitos do curso."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Algoritmos e Programação", 60, [], EMENTA_PADRAO, grad)
    curso_base = sistema_limpo.cursos[0]

    sistema_limpo.cadastrar_curso("Programação Orientada a Objetos", 60, [curso_base], EMENTA_PADRAO, grad)
    curso_avancado = sistema_limpo.cursos[1]

    sistema_limpo.abrir_turma(f"{ano}.2", {"ter": "10:00-12:00"}, 25, "Lab 01", curso_avancado)
    turma_avancada = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Ana Beatriz", CPFS_VALIDOS[0], "88999990001", "ana@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    with pytest.raises(ValueError, match="Pré-requisito não atendido"):
        sistema_limpo.realizar_matricula(aluno, turma_avancada)


def test_06_matricula_permitida_apos_cumprir_pre_requisito(sistema_limpo: Sistema) -> None:
    """Verifica que o aluno aprovado no pré-requisito fica apto a cursar a disciplina dependente."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Algoritmos e Programação", 60, [], EMENTA_PADRAO, grad)
    curso_base = sistema_limpo.cursos[0]

    sistema_limpo.cadastrar_curso("Programação Orientada a Objetos", 60, [curso_base], EMENTA_PADRAO, grad)
    curso_avancado = sistema_limpo.cursos[1]

    sistema_limpo.abrir_turma(f"{ano}.1", {"seg": "08:00-10:00"}, 25, "Sala 01", curso_base)
    turma_base = sistema_limpo.turmas[0]

    sistema_limpo.abrir_turma(f"{ano}.2", {"ter": "10:00-12:00"}, 25, "Lab 02", curso_avancado)
    turma_avancada = sistema_limpo.turmas[1]

    sistema_limpo.cadastrar_aluno("Carlos Eduardo", CPFS_VALIDOS[0], "88999990001", "carlos@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    # Cursa e obtém aprovação na disciplina base.
    sistema_limpo.realizar_matricula(aluno, turma_base)
    sistema_limpo.lancar_nota_aluno(aluno.cpf, turma_base.id_turma, "AV1", 8.0)
    sistema_limpo.lancar_nota_aluno(aluno.cpf, turma_base.id_turma, "AV2", 9.0)
    sistema_limpo.lancar_frequencia_aluno(aluno.cpf, turma_base.id_turma, 50)
    sistema_limpo.consolidar_situacao_turma(turma_base.id_turma)

    assert aluno.historico[0].status == "Aprovado"

    # Agora a matrícula na disciplina avançada deve ser permitida.
    sistema_limpo.realizar_matricula(aluno, turma_avancada)
    assert len(aluno.historico) == 2


def test_07_matricula_negada_choque_horario(sistema_limpo: Sistema) -> None:
    """Impede a matrícula quando há coincidência de dia e horário com outra turma em curso."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Matemática Discreta", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.cadastrar_curso("Lógica para Computação", 60, [], EMENTA_PADRAO, grad)

    horario_conflitante = {"seg": "08:00-10:00", "qua": "08:00-10:00"}
    sistema_limpo.abrir_turma(f"{ano}.2", horario_conflitante, 20, "Sala 10", sistema_limpo.cursos[0])
    sistema_limpo.abrir_turma(f"{ano}.2", horario_conflitante, 20, "Sala 12", sistema_limpo.cursos[1])

    sistema_limpo.cadastrar_aluno("Fernanda Lima", CPFS_VALIDOS[0], "88999990001", "fernanda@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    sistema_limpo.realizar_matricula(aluno, sistema_limpo.turmas[0])

    with pytest.raises(ValueError, match="Choque de horário"):
        sistema_limpo.realizar_matricula(aluno, sistema_limpo.turmas[1])


def test_08_matricula_negada_turma_lotada(sistema_limpo: Sistema) -> None:
    """Impede novas matrículas quando a ocupação da turma atinge o limite máximo de vagas."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Redes de Computadores", 60, [], EMENTA_PADRAO, grad)
    curso = sistema_limpo.cursos[0]

    # Abre turma com apenas 1 vaga disponível.
    sistema_limpo.abrir_turma(f"{ano}.2", {"sex": "14:00-16:00"}, 1, "Lab Redes", curso)
    turma = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Aluno Um", CPFS_VALIDOS[0], "88999990001", "um@ufca.edu.br", grad)
    sistema_limpo.cadastrar_aluno("Aluno Dois", CPFS_VALIDOS[1], "88999990002", "dois@ufca.edu.br", grad)

    sistema_limpo.realizar_matricula(sistema_limpo.alunos[0], turma)

    with pytest.raises(ValueError, match="limite máximo de 1 vagas"):
        sistema_limpo.realizar_matricula(sistema_limpo.alunos[1], turma)


def test_09_matricula_negada_turma_fechada(sistema_limpo: Sistema) -> None:
    """Garante que não é possível realizar matrículas em turmas com status 'Fechada'."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Sistemas Operacionais", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"qui": "14:00-16:00"}, 20, "Sala 05", sistema_limpo.cursos[0])
    turma = sistema_limpo.turmas[0]

    # Altera o estado da turma para Fechada.
    turma.status = "Fechada"

    sistema_limpo.cadastrar_aluno("Lucas Mendes", CPFS_VALIDOS[0], "88999990001", "lucas@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    with pytest.raises(ValueError, match="Fechada"):
        sistema_limpo.realizar_matricula(aluno, turma)


def test_10_matricula_negada_limite_maximo_turmas_simultaneas(sistema_limpo: Sistema) -> None:
    """Testa o bloqueio de matrícula quando o aluno atinge max_turmas_por_aluno (3 no fixture)."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    dias = ["seg", "ter", "qua", "qui"]
    nomes_cursos = [
        "Engenharia de Requisitos",
        "Qualidade de Software",
        "Arquitetura de Software",
        "Gerência de Projetos"
    ]

    for indice, nome_c in enumerate(nomes_cursos):
        sistema_limpo.cadastrar_curso(nome_c, 60, [], EMENTA_PADRAO, grad)
        sistema_limpo.abrir_turma(
            f"{ano}.2",
            {dias[indice]: "08:00-10:00"},
            20,
            f"Sala {indice + 1}",
            sistema_limpo.cursos[indice]
        )

    sistema_limpo.cadastrar_aluno("Beatriz Rocha", CPFS_VALIDOS[0], "88999990001", "bia@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    # Matricula nas 3 primeiras turmas (limite configurado no fixture = 3).
    for i in range(3):
        sistema_limpo.realizar_matricula(aluno, sistema_limpo.turmas[i])

    # A 4ª matrícula simultânea deve ser barrada.
    with pytest.raises(ValueError, match="limite máximo de 3 turmas simultâneas"):
        sistema_limpo.realizar_matricula(aluno, sistema_limpo.turmas[3])


# Testes de Acompanhamento Acadêmico (Notas, Frequência, Situação e Trancamento)

def test_11_lancamento_notas_frequencia_e_aprovacao(sistema_limpo: Sistema) -> None:
    """Verifica o cálculo da Média Final (MF), percentual de frequência e aprovação."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Compiladores Aplicados", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"seg": "10:00-12:00"}, 20, "Sala 09", sistema_limpo.cursos[0])
    sistema_limpo.cadastrar_aluno("Rafael Costa", CPFS_VALIDOS[0], "88999990001", "rafa@ufca.edu.br", grad)

    aluno = sistema_limpo.alunos[0]
    turma = sistema_limpo.turmas[0]

    sistema_limpo.realizar_matricula(aluno, turma)
    sistema_limpo.lancar_nota_aluno(aluno.matricula, turma.id_turma, "AV1", 7.5)
    sistema_limpo.lancar_nota_aluno(aluno.matricula, turma.id_turma, "AV2", 8.5)
    sistema_limpo.lancar_frequencia_aluno(aluno.matricula, turma.id_turma, 48)  # 48/60 = 80%

    matricula = aluno.historico[0]
    assert matricula.notas["MF"] == 8.0
    assert matricula.frequencia == 80.0

    sistema_limpo.consolidar_situacao_turma(turma.id_turma)
    assert matricula.status == "Aprovado"


def test_12_reprovacao_por_nota_e_por_frequencia(sistema_limpo: Sistema) -> None:
    """Verifica os cenários de reprovação por nota, por falta e por ambos simultaneamente."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Inteligência Artificial", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"qua": "10:00-12:00"}, 20, "Lab IA", sistema_limpo.cursos[0])
    turma = sistema_limpo.turmas[0]

    for idx in range(3):
        sistema_limpo.cadastrar_aluno(
            f"Estudante Teste {idx + 1}",
            CPFS_VALIDOS[idx],
            f"8899999000{idx + 1}",
            f"estudante{idx + 1}@ufca.edu.br",
            grad
        )
        sistema_limpo.realizar_matricula(sistema_limpo.alunos[idx], turma)

    # Aluno 0: Nota baixa (5.0) e frequência alta (50h = 83.33%) -> Reprovado por Nota.
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[0].cpf, turma.id_turma, "AV1", 4.0)
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[0].cpf, turma.id_turma, "AV2", 6.0)
    sistema_limpo.lancar_frequencia_aluno(sistema_limpo.alunos[0].cpf, turma.id_turma, 50)

    # Aluno 1: Nota alta (9.0) e frequência baixa (30h = 50.0%) -> Reprovado por Falta.
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[1].cpf, turma.id_turma, "AV1", 9.0)
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[1].cpf, turma.id_turma, "AV2", 9.0)
    sistema_limpo.lancar_frequencia_aluno(sistema_limpo.alunos[1].cpf, turma.id_turma, 30)

    # Aluno 2: Nota baixa (3.0) e frequência baixa (20h = 33.33%) -> Reprovado por Falta e por Nota.
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[2].cpf, turma.id_turma, "AV1", 2.0)
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[2].cpf, turma.id_turma, "AV2", 4.0)
    sistema_limpo.lancar_frequencia_aluno(sistema_limpo.alunos[2].cpf, turma.id_turma, 20)

    sistema_limpo.consolidar_situacao_turma(turma.id_turma)

    assert sistema_limpo.alunos[0].historico[0].status == "Reprovado por Nota"
    assert sistema_limpo.alunos[1].historico[0].status == "Reprovado por Falta"
    assert sistema_limpo.alunos[2].historico[0].status == "Reprovado por Falta e por Nota"


def test_13_trancamento_matricula_dentro_e_fora_do_prazo(sistema_limpo: Sistema) -> None:
    """Testa o trancamento de disciplina dentro da data-limite e o bloqueio após o prazo."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Computação Gráfica", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"sex": "08:00-10:00"}, 10, "Lab CG", sistema_limpo.cursos[0])
    turma = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Aluno Trancamento", CPFS_VALIDOS[0], "88999990001", "tranca@ufca.edu.br", grad)
    sistema_limpo.cadastrar_aluno("Aluno Fora Prazo", CPFS_VALIDOS[1], "88999990002", "prazo@ufca.edu.br", grad)

    aluno_ok = sistema_limpo.alunos[0]
    aluno_atrasado = sistema_limpo.alunos[1]

    sistema_limpo.realizar_matricula(aluno_ok, turma)
    sistema_limpo.realizar_matricula(aluno_atrasado, turma)
    assert len(turma) == 2

    # Trancamento dentro do prazo válido deve liberar a vaga na turma.
    sistema_limpo.trancar_matricula_aluno(aluno_ok.cpf, turma.id_turma)
    assert aluno_ok.historico[0].status == "Trancada"
    assert len(turma) == 1

    # Simula expiração da data-limite de trancamento para ontem.
    sistema_limpo.configuracao._data_limite_trancamento = date.today() - timedelta(days=1)

    with pytest.raises(ValueError, match="Período de trancamento encerrado"):
        sistema_limpo.trancar_matricula_aluno(aluno_atrasado.cpf, turma.id_turma)


# Testes de Cálculo de CR, Métodos Especiais e Relatórios Acadêmicos

def test_14_calculo_cr_media_ponderada_e_ordenacao_lt(sistema_limpo: Sistema) -> None:
    """Testa o cálculo do CR ponderado por carga horária e a ordenação via Aluno.__lt__."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    # Curso 1 (30h) e Curso 2 (60h) para testar ponderação real.
    sistema_limpo.cadastrar_curso("Ética em Computação", 30, [], EMENTA_PADRAO, grad)
    sistema_limpo.cadastrar_curso("Engenharia de Dados", 60, [], EMENTA_PADRAO, grad)

    sistema_limpo.abrir_turma(f"{ano}.2", {"seg": "08:00-10:00"}, 20, "Sala 1", sistema_limpo.cursos[0])
    sistema_limpo.abrir_turma(f"{ano}.2", {"ter": "08:00-10:00"}, 20, "Sala 2", sistema_limpo.cursos[1])

    sistema_limpo.cadastrar_aluno("Gabriel Santos", CPFS_VALIDOS[0], "88999990001", "gabriel@ufca.edu.br", grad)
    sistema_limpo.cadastrar_aluno("Amanda Borges", CPFS_VALIDOS[1], "88999990002", "amanda@ufca.edu.br", grad)

    gabriel = sistema_limpo.alunos[0]
    amanda = sistema_limpo.alunos[1]

    # Gabriel: nota 6.0 em 30h e nota 9.0 em 60h -> CR = (6*30 + 9*60) / 90 = 720 / 90 = 8.0
    sistema_limpo.realizar_matricula(gabriel, sistema_limpo.turmas[0])
    sistema_limpo.realizar_matricula(gabriel, sistema_limpo.turmas[1])
    sistema_limpo.lancar_nota_aluno(gabriel.cpf, sistema_limpo.turmas[0].id_turma, "AV1", 6.0)
    sistema_limpo.lancar_nota_aluno(gabriel.cpf, sistema_limpo.turmas[0].id_turma, "AV2", 6.0)
    sistema_limpo.lancar_nota_aluno(gabriel.cpf, sistema_limpo.turmas[1].id_turma, "AV1", 9.0)
    sistema_limpo.lancar_nota_aluno(gabriel.cpf, sistema_limpo.turmas[1].id_turma, "AV2", 9.0)

    # Amanda: nota 9.5 em 60h -> CR = 9.5
    sistema_limpo.realizar_matricula(amanda, sistema_limpo.turmas[1])
    sistema_limpo.lancar_nota_aluno(amanda.cpf, sistema_limpo.turmas[1].id_turma, "AV1", 9.5)
    sistema_limpo.lancar_nota_aluno(amanda.cpf, sistema_limpo.turmas[1].id_turma, "AV2", 9.5)

    assert gabriel.cr == 8.0
    assert amanda.cr == 9.5
    assert gabriel < amanda


def test_15_relatorio_alunos_turma_e_ocupacao(sistema_limpo: Sistema, capsys: pytest.CaptureFixture) -> None:
    """Verifica a saída formatada do relatório de alunos por turma e ocupação de vagas."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Segurança da Informação", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"qua": "14:00-16:00"}, 10, "Sala Seg", sistema_limpo.cursos[0])
    turma = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Vinícius Oliveira", CPFS_VALIDOS[0], "88999990001", "vini@ufca.edu.br", grad)
    sistema_limpo.realizar_matricula(sistema_limpo.alunos[0], turma)

    sistema_limpo.gerar_relatorio_alunos_turma(turma.id_turma)
    saida = capsys.readouterr().out

    assert "RELATÓRIO DE OCUPAÇÃO DA TURMA" in saida
    assert "1 de 10 vagas (10.0%)" in saida
    assert "Vinícius Olivei" in saida


def test_16_relatorio_distribuicao_notas_e_taxa_aprovacao(
    sistema_limpo: Sistema, capsys: pytest.CaptureFixture
) -> None:
    """Testa o cálculo de média, mediana, desvio padrão e taxa de aprovação após encerramento."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Cálculo Numérico", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"seg": "14:00-16:00"}, 10, "Sala Calc", sistema_limpo.cursos[0])
    turma = sistema_limpo.turmas[0]

    # Matricula 5 alunos (quórum mínimo para encerrar turma) com 4 aprovados e 1 reprovado.
    notas_finais = [5.0, 7.0, 8.0, 9.0, 10.0]
    for i in range(5):
        sistema_limpo.cadastrar_aluno(
            f"Aluno Calculo {i + 1}",
            CPFS_VALIDOS[i],
            f"8899999000{i + 1}",
            f"calc{i + 1}@ufca.edu.br",
            grad
        )
        aluno = sistema_limpo.alunos[i]
        sistema_limpo.realizar_matricula(aluno, turma)
        sistema_limpo.lancar_nota_aluno(aluno.cpf, turma.id_turma, "AV1", notas_finais[i])
        sistema_limpo.lancar_nota_aluno(aluno.cpf, turma.id_turma, "AV2", notas_finais[i])
        sistema_limpo.lancar_frequencia_aluno(aluno.cpf, turma.id_turma, 50)

    sistema_limpo.encerrar_turma(turma.id_turma)
    assert turma.status == "Fechada"

    sistema_limpo.gerar_relatorio_distribuicao_notas(turma.id_turma)
    sistema_limpo.gerar_relatorio_taxa_aprovacao()
    saida = capsys.readouterr().out

    # Média de [5, 7, 8, 9, 10] = 7.80 | Mediana = 8.00 | Taxa de aprovação = 4/5 = 80.00%.
    assert "Média Aritmética: 7.80" in saida
    assert "Mediana: 8.00" in saida
    assert "Taxa de Aprovação Global: 80.00%" in saida


def test_17_relatorio_alunos_risco_e_top_n_periodo(
    sistema_limpo: Sistema, capsys: pytest.CaptureFixture
) -> None:
    """Verifica a listagem de alunos em risco (nota/frequência) e o ranking Top N por período."""

    ano = date.today().year
    periodo = f"{ano}.2"
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Interação Humano Computador", 60, [], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(periodo, {"qui": "08:00-10:00"}, 15, "Sala IHC", sistema_limpo.cursos[0])
    turma = sistema_limpo.turmas[0]

    # Cadastra 3 alunos.
    nomes = ["Danilo Nunes", "Diêgo Carvalho", "Maria Luíza"]
    for i, nome in enumerate(nomes):
        sistema_limpo.cadastrar_aluno(nome, CPFS_VALIDOS[i], f"8899999000{i + 1}", f"al{i}@ufca.edu.br", grad)
        sistema_limpo.realizar_matricula(sistema_limpo.alunos[i], turma)

    # Aluno 0 em risco por nota (MF 5.0 < 7.0) e por falta (20h = 33.3% < 75%).
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[0].cpf, turma.id_turma, "AV1", 5.0)
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[0].cpf, turma.id_turma, "AV2", 5.0)
    sistema_limpo.lancar_frequencia_aluno(sistema_limpo.alunos[0].cpf, turma.id_turma, 20)

    sistema_limpo.gerar_relatorio_alunos_risco()
    saida_risco = capsys.readouterr().out
    assert "Danilo Nunes" in saida_risco

    # Aprova Alunos 1 e 2 para testar o Top N (top_n_alunos = 2 no fixture).
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[1].cpf, turma.id_turma, "AV1", 8.5)
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[1].cpf, turma.id_turma, "AV2", 8.5)
    sistema_limpo.lancar_frequencia_aluno(sistema_limpo.alunos[1].cpf, turma.id_turma, 50)

    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[2].cpf, turma.id_turma, "AV1", 9.5)
    sistema_limpo.lancar_nota_aluno(sistema_limpo.alunos[2].cpf, turma.id_turma, "AV2", 9.5)
    sistema_limpo.lancar_frequencia_aluno(sistema_limpo.alunos[2].cpf, turma.id_turma, 50)

    sistema_limpo.consolidar_situacao_turma(turma.id_turma)
    sistema_limpo.gerar_relatorio_top_n(periodo)
    saida_top = capsys.readouterr().out

    assert "1º LUGAR: Maria Luíza" in saida_top
    assert "2º LUGAR: Diêgo Carvalho" in saida_top


# Testes de Atualização (UPDATE), Soft Delete e Persistência em JSON

def test_18_atualizacao_parcial_crud_e_regra_carga_horaria_ementa(sistema_limpo: Sistema) -> None:
    """Testa atualizações parciais de entidades e a proibição de alterar carga horária sem ementa."""

    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Teste e Qualidade", 60, [], EMENTA_PADRAO, grad)
    curso = sistema_limpo.cursos[0]

    # Tentar atualizar a carga horária sem enviar nova ementa deve falhar.
    with pytest.raises(ValueError, match="sem atualizar a ementa"):
        sistema_limpo.atualizar_curso(curso.codigo, nova_carga_horaria=80)

    # Atualizar ambos simultaneamente (sem turmas abertas) deve funcionar.
    sistema_limpo.atualizar_curso(curso.codigo, nova_carga_horaria=80, nova_ementa=EMENTA_ATUALIZADA)
    assert curso.carga_horaria == 80

    # Atualização parcial de aluno (apenas telefone).
    sistema_limpo.cadastrar_aluno("José Felipe", CPFS_VALIDOS[0], "88999990001", "jose@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]
    sistema_limpo.atualizar_aluno(aluno.cpf, novo_telefone="88988887777")
    assert aluno.telefone == "88988887777"
    assert aluno.email == "jose@ufca.edu.br"


def test_19_soft_delete_inativacoes_e_travas_seguranca(sistema_limpo: Sistema) -> None:
    """Testa as travas de segurança do Soft Delete (impedindo órfãos) e a inativação após conclusão."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Programação Web", 60, [], EMENTA_PADRAO, grad)
    curso = sistema_limpo.cursos[0]

    sistema_limpo.abrir_turma(f"{ano}.2", {"sex": "10:00-12:00"}, 20, "Lab Web", curso)
    turma = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Gledson Alves", CPFS_VALIDOS[0], "88999990001", "gledson@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]
    sistema_limpo.realizar_matricula(aluno, turma)

    # Não deve permitir inativar aluno com disciplina 'Cursando'.
    with pytest.raises(ValueError, match="possui disciplinas em andamento"):
        sistema_limpo.inativar_aluno(aluno.cpf)

    # Não deve permitir inativar curso com turma 'Aberta'.
    with pytest.raises(ValueError, match="possui turmas abertas"):
        sistema_limpo.inativar_curso(curso.codigo)

    # Não deve permitir inativar graduação com curso ativo.
    with pytest.raises(ValueError, match="possui disciplinas ativas"):
        sistema_limpo.inativar_graduacao(grad.codigo_mec)

    # Após trancar a matrícula e inativar na ordem correta, o Soft Delete é concluído.
    sistema_limpo.trancar_matricula_aluno(aluno.cpf, turma.id_turma)
    sistema_limpo.inativar_aluno(aluno.cpf)
    sistema_limpo.inativar_turma(turma.id_turma)
    sistema_limpo.inativar_curso(curso.codigo)
    sistema_limpo.inativar_graduacao(grad.codigo_mec)

    assert not aluno.ativo
    assert not turma.ativo
    assert not curso.ativo
    assert not grad.ativo
    assert sistema_limpo.buscar_aluno(aluno.cpf) is None


def test_20_persistencia_json_salvar_e_carregar_estado(sistema_limpo: Sistema) -> None:
    """Garante que salvar_estado e carregar_estado reconstroem todos os vínculos e metadados."""

    ano = date.today().year
    sistema_limpo.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad = sistema_limpo.graduacoes[0]

    sistema_limpo.cadastrar_curso("Algoritmos Base", 60, [], EMENTA_PADRAO, grad)
    c1 = sistema_limpo.cursos[0]

    sistema_limpo.cadastrar_curso("Estrutura Avançada", 60, [c1], EMENTA_PADRAO, grad)
    sistema_limpo.abrir_turma(f"{ano}.2", {"seg": "08:00-10:00"}, 25, "Sala 10", c1)
    turma = sistema_limpo.turmas[0]

    sistema_limpo.cadastrar_aluno("Évyla Silva", CPFS_VALIDOS[0], "88999990001", "evyla@ufca.edu.br", grad)
    aluno = sistema_limpo.alunos[0]

    sistema_limpo.realizar_matricula(aluno, turma)
    sistema_limpo.lancar_nota_aluno(aluno.cpf, turma.id_turma, "AV1", 9.0)
    sistema_limpo.lancar_nota_aluno(aluno.cpf, turma.id_turma, "AV2", 10.0)
    sistema_limpo.lancar_frequencia_aluno(aluno.cpf, turma.id_turma, 54)

    # Salva tudo nos ficheiros JSON e instancia um novo Sistema a partir do disco.
    sistema_limpo.salvar_estado()

    novo_sistema = Sistema(sistema_limpo.configuracao)

    assert len(novo_sistema.graduacoes) == 1
    assert len(novo_sistema.cursos) == 2
    assert novo_sistema.cursos[1].pre_requisitos[0].codigo == c1.codigo
    assert len(novo_sistema.turmas) == 1
    assert len(novo_sistema.alunos) == 1
    assert len(novo_sistema.matriculas) == 1

    aluno_recarregado = novo_sistema.alunos[0]
    assert aluno_recarregado.cr == 9.5
    assert aluno_recarregado.historico[0].frequencia == 90.0