# noinspection SpellCheckingInspection
import sys
import json
import argparse
from datetime import date, timedelta
from pathlib import Path

from src.config.config import Configuracao
from src.services.sistema import Sistema


# Funções Auxiliares de Inicialização e Conversão

def carregar_configuracao(caminho_settings: str = "data/settings.json") -> Configuracao:
    """
    Verifica a existência do arquivo settings.json no disco e instancia Configuracao.
    Caso o arquivo ainda não exista, cria-o automaticamente com parâmetros padrão.
    """

    caminho_arquivo = Path(caminho_settings)

    # Cria o arquivo de configurações padrão caso não exista no diretório 'data/'.
    if not caminho_arquivo.exists():
        caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        ano_atual = date.today().year
        semestre_atual = 1 if date.today().month <= 6 else 2
        data_limite = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")

        dados_padrao = {
            "nota_minima_aprovacao": 7.0,
            "frequencia_minima": 75.0,
            "data_limite_trancamento": data_limite,
            "max_turmas_por_aluno": 7,
            "top_n_alunos": 10,
            "semestre_vigente": f"{ano_atual}.{semestre_atual}"
        }

        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(dados_padrao, arquivo, indent=4, ensure_ascii=False)

    # Instancia Configuracao passando o caminho textual conforme definido em config.py.
    return Configuracao(str(caminho_arquivo))


def converter_horarios(horarios_str: str) -> dict:
    """
    Converte uma string de horários (JSON ou formato 'ter=10:00-12:00,qui=10:00-12:00')
    em um dicionário Python válido para as turmas.
    """

    texto = horarios_str.strip()

    # Se o operador passou em formato JSON direto (ex: '{"ter": "10:00-12:00"}').
    if texto.startswith("{"):
        try:
            return json.loads(texto)
        except json.JSONDecodeError as erro:
            raise ValueError(f"Formato JSON inválido para horários! Detalhe: {erro}")

    # Se o operador passou no formato simplificado 'dia=hora,dia=hora'.
    dicionario_horarios = {}
    for par in texto.split(","):
        if "=" in par:
            dia, intervalo = par.split("=", 1)
            dicionario_horarios[dia.strip().lower()] = intervalo.strip()
        elif ":" in par and "-" in par:
            # Suporte alternativo para 'ter:10:00-12:00'.
            dia, intervalo = par.split(":", 1)
            dicionario_horarios[dia.strip().lower()] = intervalo.strip()

    if not dicionario_horarios:
        raise ValueError(
            "Formato de horários inválido! Utilize 'ter=08:00-10:00,qui=08:00-10:00' "
            "ou JSON '{\"ter\": \"08:00-10:00\"}'."
        )

    return dicionario_horarios


def executar_seed(sistema: Sistema) -> None:
    """Popula o sistema com um conjunto inicial de dados de demonstração (Rotina de Seed)."""

    if sistema.graduacoes:
        print("Aviso: O sistema já possui dados cadastrados. A rotina de seed foi ignorada.")
        return None

    ano_atual = date.today().year
    periodo_exemplo = f"{ano_atual}.2"

    # Cadastra Graduação e garante a tipagem para o analisador estático.
    sistema.cadastrar_graduacao("12345678", "Engenharia de Software", 8)
    grad_es = sistema.buscar_graduacao("12345678")

    if grad_es is None:
        raise ValueError("Erro interno ao recuperar a graduação cadastrada durante o seed!")

    # Cadastra Cursos (Disciplinas) com ementas >= 100 caracteres.
    ementa_alg = (
        "Introdução à lógica de programação, estruturas condicionais, laços de repetição, "
        "vetores, matrizes, funções e modularização de algoritmos computacionais."
    )
    ementa_poo = (
        "Conceitos fundamentais de Programação Orientada a Objetos: classes, objetos, "
        "encapsulamento, herança, polimorfismo, métodos especiais e tratamento de exceções."
    )

    sistema.cadastrar_curso("Algoritmos e Programação", 60, [], ementa_alg, grad_es)
    curso_alg = sistema.cursos[0]

    sistema.cadastrar_curso("Programação Orientada a Objetos", 60, [curso_alg], ementa_poo, grad_es)
    curso_poo = sistema.cursos[1]

    # Abre Turmas.
    sistema.abrir_turma(
        periodo_exemplo,
        {"seg": "08:00-10:00", "qua": "08:00-10:00"},
        30,
        "Bloco I - Sala 10",
        curso_alg
    )
    sistema.abrir_turma(
        periodo_exemplo,
        {"ter": "10:00-12:00", "qui": "10:00-12:00"},
        25,
        "Laboratório 02",
        curso_poo
    )
    turma_alg = sistema.turmas[0]

    # Cadastra Alunos com CPFs matematicamente válidos.
    dados_alunos = [
        ("Ana Beatriz Souza", "52998224725", "88999990001", "ana.souza@ufca.edu.br"),
        ("Carlos Eduardo Lima", "11144477735", "88999990002", "carlos.lima@ufca.edu.br"),
        ("Fernanda Oliveira", "12345678909", "88999990003", "fernanda.oli@ufca.edu.br")
    ]

    for nome, cpf, tel, email in dados_alunos:
        sistema.cadastrar_aluno(nome, cpf, tel, email, grad_es)

    # Realiza Matrículas e Lançamentos iniciais na turma de Algoritmos.
    for indice, aluno in enumerate(sistema.alunos):
        sistema.realizar_matricula(aluno, turma_alg)
        sistema.lancar_nota_aluno(aluno.matricula, turma_alg.id_turma, "AV1", 7.0 + indice)
        sistema.lancar_nota_aluno(aluno.matricula, turma_alg.id_turma, "AV2", 8.0 + indice)
        sistema.lancar_frequencia_aluno(aluno.matricula, turma_alg.id_turma, 50)

    sistema.salvar_estado()
    print("Base de dados inicial (Seed) gerada e persistida com sucesso!")
    return None



# Construção do Parser de Subcomandos (CLI)

def construir_parser() -> argparse.ArgumentParser:
    """Configura todos os subcomandos e argumentos da Interface de Linha de Comandos."""

    parser = argparse.ArgumentParser(
        prog="acad",
        description="Sistema de Gestão Acadêmica Universitária (DDD / CLI)"
    )

    subparsers = parser.add_subparsers(dest="comando", help="Subcomandos disponíveis")

    # --- Subcomandos CREATE ---
    p_cad_grad = subparsers.add_parser("cadastrar-graduacao", help="Cadastra uma nova graduação")
    p_cad_grad.add_argument("--codigo-mec", required=True, help="Código MEC de 8 dígitos")
    p_cad_grad.add_argument("--nome", required=True, help="Nome da graduação")
    p_cad_grad.add_argument("--semestres", required=True, type=int, help="Duração em semestres (3 a 12)")

    p_cad_curso = subparsers.add_parser("cadastrar-curso", help="Cadastra um novo curso (disciplina)")
    p_cad_curso.add_argument("--nome", required=True, help="Nome da disciplina")
    p_cad_curso.add_argument("--carga-horaria", required=True, type=int, help="Carga horária total em horas")
    p_cad_curso.add_argument("--ementa", required=True, help="Texto da ementa (mínimo 100 caracteres)")
    p_cad_curso.add_argument("--graduacao", required=True, help="Código MEC da graduação vinculada")
    p_cad_curso.add_argument("--pre-requisitos", nargs="*", default=[], help="Lista de códigos de pré-requisitos")

    p_abrir_turma = subparsers.add_parser("abrir-turma", help="Abre uma nova oferta de turma")
    p_abrir_turma.add_argument("--curso", required=True, help="Código do curso ofertado")
    p_abrir_turma.add_argument("--periodo", required=True, help="Período letivo (ex: 2026.2)")
    p_abrir_turma.add_argument("--horarios", required=True, help="Ex: 'ter=10:00-12:00,qui=10:00-12:00' ou JSON")
    p_abrir_turma.add_argument("--vagas", required=True, type=int, help="Limite máximo de vagas")
    p_abrir_turma.add_argument("--local", required=True, help="Sala ou laboratório")

    p_cad_aluno = subparsers.add_parser("cadastrar-aluno", help="Cadastra um novo aluno")
    p_cad_aluno.add_argument("--nome", required=True, help="Nome completo do aluno")
    p_cad_aluno.add_argument("--cpf", required=True, help="CPF válido (11 dígitos)")
    p_cad_aluno.add_argument("--telefone", required=True, help="Telefone com DDD (11 dígitos)")
    p_cad_aluno.add_argument("--email", required=True, help="Endereço de e-mail")
    p_cad_aluno.add_argument("--graduacao", required=True, help="Código MEC da graduação pretendida")

    p_matricular = subparsers.add_parser("matricular", help="Matricula um aluno em uma turma aberta")
    p_matricular.add_argument("--aluno", required=True, help="CPF ou Matrícula do aluno")
    p_matricular.add_argument("--turma", required=True, help="ID da turma")

    # --- Subcomandos READ (Consultas e Listagens) ---
    p_buscar = subparsers.add_parser("buscar", help="Busca um registro ativo pelo identificador")
    p_buscar.add_argument("entidade", choices=["aluno", "curso", "turma", "graduacao"], help="Tipo de entidade")
    p_buscar.add_argument("identificador", help="CPF/Matrícula, Código do Curso, ID da Turma ou Código MEC")

    p_listar = subparsers.add_parser("listar", help="Lista todos os registros ativos de uma categoria")
    p_listar.add_argument("entidade", choices=["alunos", "cursos", "turmas", "graduacoes"], help="Categoria")

    # --- Subcomandos UPDATE (Acompanhamento Acadêmico e Atualizações) ---
    p_nota = subparsers.add_parser("lancar-nota", help="Lança nota (AV1 ou AV2) para um aluno em uma turma")
    p_nota.add_argument("--aluno", required=True, help="CPF ou Matrícula do aluno")
    p_nota.add_argument("--turma", required=True, help="ID da turma")
    p_nota.add_argument("--avaliacao", required=True, choices=["AV1", "AV2", "av1", "av2"], help="AV1 ou AV2")
    p_nota.add_argument("--nota", required=True, type=float, help="Valor da nota (0 a 10)")

    p_freq = subparsers.add_parser("lancar-frequencia", help="Contabiliza horas-aula assistidas pelo aluno")
    p_freq.add_argument("--aluno", required=True, help="CPF ou Matrícula do aluno")
    p_freq.add_argument("--turma", required=True, help="ID da turma")
    p_freq.add_argument("--horas", required=True, type=int, help="Quantidade de horas assistidas")

    p_trancar = subparsers.add_parser(
        "trancar-matricula",
        help="Realiza o trancamento de uma disciplina dentro do prazo"
    )
    p_trancar.add_argument("--aluno", required=True, help="CPF ou Matrícula do aluno")
    p_trancar.add_argument("--turma", required=True, help="ID da turma")

    p_encerrar = subparsers.add_parser("encerrar-turma", help="Consolida situações finais e fecha a turma")
    p_encerrar.add_argument("--turma", required=True, help="ID da turma")

    p_att_aluno = subparsers.add_parser("atualizar-aluno", help="Atualiza parcialmente os dados de um aluno")
    p_att_aluno.add_argument("--id", required=True, help="CPF ou Matrícula do aluno")
    p_att_aluno.add_argument("--nome", default=None, help="Novo nome")
    p_att_aluno.add_argument("--telefone", default=None, help="Novo telefone")
    p_att_aluno.add_argument("--email", default=None, help="Novo e-mail")

    p_att_curso = subparsers.add_parser("atualizar-curso", help="Atualiza dados de um curso ativo")
    p_att_curso.add_argument("--codigo", required=True, help="Código do curso")
    p_att_curso.add_argument("--nome", default=None, help="Novo nome")
    p_att_curso.add_argument("--carga-horaria", type=int, default=None, help="Nova carga horária (exige --ementa)")
    p_att_curso.add_argument("--ementa", default=None, help="Nova ementa")

    p_att_turma = subparsers.add_parser("atualizar-turma", help="Atualiza local, vagas ou horários de uma turma")
    p_att_turma.add_argument("--turma", required=True, help="ID da turma")
    p_att_turma.add_argument("--local", default=None, help="Novo local")
    p_att_turma.add_argument("--vagas", type=int, default=None, help="Nova capacidade de vagas")
    p_att_turma.add_argument("--horarios", default=None, help="Novos dias e horários")

    p_att_grad = subparsers.add_parser("atualizar-graduacao", help="Atualiza dados de uma graduação")
    p_att_grad.add_argument("--codigo-mec", required=True, help="Código MEC da graduação")
    p_att_grad.add_argument("--nome", default=None, help="Novo nome")
    p_att_grad.add_argument("--semestres", type=int, default=None, help="Nova duração em semestres")

    # --- Subcomandos DELETE (Soft Delete) ---
    p_inativar = subparsers.add_parser("inativar", help="Inativa logicamente (Soft Delete) um registro")
    p_inativar.add_argument("entidade", choices=["aluno", "curso", "turma", "graduacao"], help="Tipo de entidade")
    p_inativar.add_argument("identificador", help="Identificador único do registro")

    # --- Subcomandos de RELATÓRIOS ---
    p_relatorio = subparsers.add_parser("relatorio", help="Gera relatórios acadêmicos e estatísticos")
    p_relatorio.add_argument(
        "tipo",
        choices=["alunos-turma", "taxa-aprovacao", "distribuicao-notas", "alunos-risco", "top-n"],
        help="Tipo de relatório desejado"
    )
    p_relatorio.add_argument("--turma", help="ID da turma (obrigatório para alunos-turma e distribuicao-notas)")
    p_relatorio.add_argument("--periodo", help="Período letivo (obrigatório para top-n, ex: 2026.2)")

    # --- Subcomando SEED ---
    subparsers.add_parser("seed", help="Popula o sistema com dados iniciais de demonstração")

    return parser


# Ponto de Entrada Principal (Orquestração da CLI)

def main() -> None:
    """Processa os argumentos de linha de comando, aciona o Sistema e persiste o estado."""

    parser = construir_parser()
    args = parser.parse_args()

    # Se nenhum subcomando foi informado, exibe o guia de ajuda.
    if not args.comando:
        parser.print_help()
        return

    try:
        # Inicializa configurações e hidrata o sistema a partir dos JSONs.
        configuracao = carregar_configuracao()
        sistema = Sistema(configuracao)

        # Roteamento dos Subcomandos
        if args.comando == "seed":
            executar_seed(sistema)

        elif args.comando == "cadastrar-graduacao":
            sistema.cadastrar_graduacao(args.codigo_mec, args.nome, args.semestres)
            sistema.salvar_estado()
            print(f"Graduação '{args.nome}' cadastrada com sucesso!")

        elif args.comando == "cadastrar-curso":
            graduacao = sistema.buscar_graduacao(args.graduacao)
            if graduacao is None:
                raise ValueError(f"Graduação '{args.graduacao}' não encontrada!")

            lista_prereqs = []
            for cod_pre in args.pre_requisitos:
                curso_pre = sistema.buscar_curso(cod_pre)
                if curso_pre is None:
                    raise ValueError(f"Curso pré-requisito '{cod_pre}' não encontrado!")
                lista_prereqs.append(curso_pre)

            sistema.cadastrar_curso(args.nome, args.carga_horaria, lista_prereqs, args.ementa, graduacao)
            sistema.salvar_estado()
            novo_curso = sistema.cursos[-1]
            print(f"Curso '{novo_curso.nome}' (Código: {novo_curso.codigo}) cadastrado com sucesso!")

        elif args.comando == "abrir-turma":
            curso = sistema.buscar_curso(args.curso)
            if curso is None:
                raise ValueError(f"Curso '{args.curso}' não encontrado!")

            dias_horarios = converter_horarios(args.horarios)
            sistema.abrir_turma(args.periodo, dias_horarios, args.vagas, args.local, curso)
            sistema.salvar_estado()
            nova_turma = sistema.turmas[-1]
            print(f"Turma '{nova_turma.id_turma}' aberta com sucesso para o curso '{curso.nome}'!")

        elif args.comando == "cadastrar-aluno":
            graduacao = sistema.buscar_graduacao(args.graduacao)
            if graduacao is None:
                raise ValueError(f"Graduação '{args.graduacao}' não encontrada!")

            sistema.cadastrar_aluno(args.nome, args.cpf, args.telefone, args.email, graduacao)
            sistema.salvar_estado()
            novo_aluno = sistema.alunos[-1]
            print(f"Aluno '{novo_aluno.nome}' (Matrícula: {novo_aluno.matricula}) cadastrado com sucesso!")

        elif args.comando == "matricular":
            aluno = sistema.buscar_aluno(args.aluno)
            if aluno is None:
                raise ValueError(f"Aluno '{args.aluno}' não encontrado ou inativo!")

            turma = sistema.buscar_turma(args.turma)
            if turma is None:
                raise ValueError(f"Turma '{args.turma}' não encontrada ou inativa!")

            sistema.realizar_matricula(aluno, turma)
            sistema.salvar_estado()
            print(f"Matrícula de '{aluno.nome}' na turma '{turma.id_turma}' realizada com sucesso!")

        elif args.comando == "lancar-nota":
            sistema.lancar_nota_aluno(args.aluno, args.turma, args.avaliacao, args.nota)
            sistema.salvar_estado()

        elif args.comando == "lancar-frequencia":
            sistema.lancar_frequencia_aluno(args.aluno, args.turma, args.horas)
            sistema.salvar_estado()

        elif args.comando == "trancar-matricula":
            sistema.trancar_matricula_aluno(args.aluno, args.turma)
            sistema.salvar_estado()

        elif args.comando == "encerrar-turma":
            sistema.encerrar_turma(args.turma)
            sistema.salvar_estado()

        elif args.comando == "buscar":
            if args.entidade == "aluno":
                obj = sistema.buscar_aluno(args.identificador)
                if obj:
                    print(
                        f"[{obj.matricula}] {obj.nome} | CPF: {obj.cpf} | "
                        f"CR: {obj.cr:.2f} | Graduação: {obj.graduacao.nome}"
                    )
            elif args.entidade == "curso":
                obj = sistema.buscar_curso(args.identificador)
                if obj:
                    print(obj)
            elif args.entidade == "turma":
                obj = sistema.buscar_turma(args.identificador)
                if obj:
                    print(
                        f"Turma {obj.id_turma} | Curso: {obj.curso.nome} | Período: {obj.periodo} | "
                        f"Status: {obj.status} | Vagas: {len(obj.matriculas_ativas)}/{obj.vagas}"
                    )
            elif args.entidade == "graduacao":
                obj = sistema.buscar_graduacao(args.identificador)
                if obj:
                    print(
                        f"[{obj.codigo_mec}] {obj.nome} ({obj.qtd_semestres} semestres) | "
                        f"Disciplinas: {len(obj.grade_curricular)}"
                    )

        elif args.comando == "listar":
            if args.entidade == "graduacoes":
                for g in [x for x in sistema.graduacoes if x.ativo]:
                    print(f"[{g.codigo_mec}] {g.nome} - {g.qtd_semestres} semestres")
            elif args.entidade == "cursos":
                for c in [x for x in sistema.cursos if x.ativo]:
                    print(f"[{c.codigo}] {c.nome} ({c.carga_horaria}h) - Graduação: {c.graduacao.nome}")
            elif args.entidade == "turmas":
                for t in [x for x in sistema.turmas if x.ativo]:
                    print(
                        f"[{t.id_turma}] {t.curso.nome} | {t.periodo} | "
                        f"{t.status} | Ocupação: {len(t.matriculas_ativas)}/{t.vagas}"
                    )
            elif args.entidade == "alunos":
                for a in [x for x in sistema.alunos if x.ativo]:
                    print(f"[{a.matricula}] {a.nome} | CPF: {a.cpf} | CR: {a.cr:.2f}")

        elif args.comando == "atualizar-aluno":
            sistema.atualizar_aluno(args.id, args.nome, args.telefone, args.email)
            sistema.salvar_estado()

        elif args.comando == "atualizar-curso":
            sistema.atualizar_curso(args.codigo, args.nome, args.carga_horaria, args.ementa)
            sistema.salvar_estado()

        elif args.comando == "atualizar-turma":
            novos_horarios = converter_horarios(args.horarios) if args.horarios else None
            sistema.atualizar_turma(args.turma, args.local, args.vagas, novos_horarios)
            sistema.salvar_estado()

        elif args.comando == "atualizar-graduacao":
            sistema.atualizar_graduacao(args.codigo_mec, args.nome, args.semestres)
            sistema.salvar_estado()

        elif args.comando == "inativar":
            if args.entidade == "aluno":
                sistema.inativar_aluno(args.identificador)
            elif args.entidade == "curso":
                sistema.inativar_curso(args.identificador)
            elif args.entidade == "turma":
                sistema.inativar_turma(args.identificador)
            elif args.entidade == "graduacao":
                sistema.inativar_graduacao(args.identificador)
            sistema.salvar_estado()

        elif args.comando == "relatorio":
            if args.tipo == "alunos-turma":
                if not args.turma:
                    raise ValueError("O relatório 'alunos-turma' exige o argumento '--turma <ID>'!")
                sistema.gerar_relatorio_alunos_turma(args.turma)

            elif args.tipo == "taxa-aprovacao":
                sistema.gerar_relatorio_taxa_aprovacao()

            elif args.tipo == "distribuicao-notas":
                if not args.turma:
                    raise ValueError("O relatório 'distribuicao-notas' exige o argumento '--turma <ID>'!")
                sistema.gerar_relatorio_distribuicao_notas(args.turma)

            elif args.tipo == "alunos-risco":
                sistema.gerar_relatorio_alunos_risco()

            elif args.tipo == "top-n":
                if not args.periodo:
                    raise ValueError("O relatório 'top-n' exige o argumento '--periodo <AAAA.S>'!")
                sistema.gerar_relatorio_top_n(args.periodo)

    except (ValueError, TypeError, KeyError, OSError) as erro:
        print(f"\n[ERRO DE VALIDAÇÃO]: {erro}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()