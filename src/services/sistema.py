import re, statistics

from src.domain.models import graduacoes
from src.domain.models.alunos import Aluno
from src.domain.models.ofertas import Oferta
from src.domain.models.pessoas import Pessoa
from src.domain.models.turmas import Turma
from src.domain.models.cursos import Curso
from src.domain.models.matriculas import Matricula
from src.domain.models.graduacoes import Graduacao
from src.config.config import Configuracao
from src.repositories.repositorio_aluno import RepositorioAluno
from src.repositories.repositorio_curso import RepositorioCurso
from src.repositories.repositorio_graduacao import RepositorioGraduacao
from src.repositories.repositorio_matricula import RepositorioMatricula
from src.repositories.repositorio_turma import RepositorioTurma



# Construção da classe.
class Sistema:
    """
    Classe principal de controle (Orquestrador / Facade).
    Garante o funcionamento da CLI, armazenando as listas de entidades em memória,
    coordenando o CRUD, validações de negócio e delegando a persistência aos repositórios.
    """


    def __init__(self, configuracao: Configuracao) -> None:

        # Atribui e valida a instância de configuração contendo as regras de negócio globais.
        self.configuracao = configuracao

        # Injeção de Dependências: Instancia as ferramentas de conexão com a base de dados (JSON).
        self.__repo_graduacao = RepositorioGraduacao()
        self.__repo_curso = RepositorioCurso()
        self.__repo_turma = RepositorioTurma()
        self.__repo_aluno = RepositorioAluno()
        self.__repo_matricula = RepositorioMatricula()

        # Inicializa as coleções vazias na memória de forma segura para evitar erros de referência.
        self._graduacoes = []
        self._cursos = []
        self._turmas = []
        self._alunos = []
        self._matriculas = []

        # Dispara o gatilho de leitura de todos os dados respeitando a ordem cronológica de dependência.
        self.carregar_estado()


    @property
    def configuracao(self):
        """Retorna as configurações atuais do sistema."""

        return self._configuracao


    @configuracao.setter
    def configuracao(self, nova_configuracao: Configuracao):
        """Define e blinda a injeção das configurações de negócio do sistema."""

        # Garante que apenas um objeto autêntico da classe Configuracao seja injetado.
        if not isinstance(nova_configuracao, Configuracao):
            raise TypeError("A configuração atribuída deve ser um objeto válido da classe 'Configuracao'!")

        self._configuracao = nova_configuracao


    # Propriedades de acesso às listas do sistema (sem setters para evitar sobrescrita acidental).

    @property
    def graduacoes(self):
        return self._graduacoes


    @property
    def cursos(self):
        return self._cursos


    @property
    def turmas(self):
        return self._turmas


    @property
    def alunos(self):
        return self._alunos


    @property
    def matriculas(self):
        return self._matriculas


    # CREATE: Métodos Orquestradores de Cadastro e Matrícula

    def cadastrar_aluno(self, nome: str, cpf: str, telefone: str, email: str, graduacao: Graduacao) -> None:
        """Adiciona um novo aluno à lista geral da instituição."""

        # Verifica se a graduação pretendida pelo aluno consta nos registros oficiais e está ativa.
        if graduacao not in self._graduacoes or not graduacao.ativo:
            raise ValueError("A graduação informada para o aluno não está cadastrada ou encontra-se inativa!")

        # Higieniza o CPF para verificar duplicidade antes de instanciar.
        cpf_limpo = re.sub(r"[^0-9]", "", cpf) if isinstance(cpf, str) else ""

        if any(aluno.cpf == cpf_limpo for aluno in self._alunos):
            raise ValueError(f"Já existe um aluno cadastrado no sistema com o CPF '{cpf_limpo}'!")

        # Instancia o aluno (acionando internamente as validações de Pessoa e geração de matrícula).
        novo_aluno = Aluno(nome, cpf, telefone, email, graduacao)

        # Registra o novo aluno na coleção em memória do sistema.
        self._alunos.append(novo_aluno)


    def cadastrar_graduacao(self, codigo_mec: str, nome: str, qtd_semestres: int) -> None:
        """Adiciona um novo curso superior à lista de graduações ofertadas pela instituição."""

        # Higieniza o código MEC para impedir duplicidade de cadastro.
        codigo_limpo = re.sub(r"[^0-9]", "", codigo_mec) if isinstance(codigo_mec, str) else ""

        if any(grad.codigo_mec == codigo_limpo for grad in self._graduacoes):
            raise ValueError(f"Já existe uma graduação cadastrada com o código MEC '{codigo_limpo}'!")

        # Instancia a nova graduação validando código MEC, nome e duração mínima/máxima.
        nova_graduacao = Graduacao(codigo_mec, nome, qtd_semestres)

        # Registra a nova graduação na coleção em memória do sistema.
        self._graduacoes.append(nova_graduacao)


    def cadastrar_curso(
        self, nome: str, carga_horaria: int, pre_requisitos: list, ementa: str, graduacao: Graduacao
    ) -> None:
        """Adiciona um novo curso (disciplina) ao catálogo disponível e vincula à graduação."""

        # Impede o cadastro de disciplinas em graduações inexistentes ou inativas no sistema.
        if graduacao not in self._graduacoes or not graduacao.ativo:
            raise ValueError(f"A graduação '{graduacao.nome}' não está cadastrada ou encontra-se inativa!")

        # Instancia o novo curso com as suas regras de carga horária e lista de pré-requisitos.
        novo_curso = Curso(nome, carga_horaria, pre_requisitos, ementa, graduacao)

        # Vincula a disciplina criada diretamente à grade curricular da graduação correspondente.
        graduacao.adicionar_disciplina(novo_curso)

        # Adiciona a disciplina ao catálogo geral de cursos do sistema.
        self._cursos.append(novo_curso)


    def abrir_turma(self, periodo: str, dias_horarios: dict, vagas: int, local: str, curso: Curso) -> None:
        """Adiciona uma nova oferta de turma vinculada a um curso específico e ativa-a no sistema."""

        # Garante que o curso ofertado pertença ao catálogo oficial do sistema e esteja ativo.
        if curso not in self._cursos or not curso.ativo:
            raise ValueError(f"O curso '{curso.nome}' não está cadastrado no catálogo ou encontra-se inativo!")

        # Instancia a turma (o construtor da Turma já a vincula automaticamente ao Curso e gera o ID).
        nova_turma = Turma(periodo, dias_horarios, vagas, local, curso)

        # Registra a nova oferta na lista geral de turmas ativas do sistema.
        self._turmas.append(nova_turma)


    def realizar_matricula(self, aluno: Aluno, turma: Turma) -> None:
        """Localiza as instâncias, executa uma rigorosa bateria de validações e vincula o Aluno à Turma."""

        # Verifica se o aluno informado pertence aos registros ativos da instituição.
        if aluno not in self._alunos or not aluno.ativo:
            raise ValueError(f"O aluno '{aluno.nome}' não está cadastrado ou encontra-se inativo no sistema!")

        # Verifica se a turma informada consta nas ofertas oficiais e está ativa.
        if turma not in self._turmas or not turma.ativo:
            raise ValueError(f"A turma '{turma.id_turma}' não está cadastrada ou foi inativada do sistema!")

        # Impede matrículas em turmas que já foram encerradas.
        if turma.status != "Aberta":
            raise ValueError(
                f"A matrícula não pode ser realizada pois a turma '{turma.id_turma}' está '{turma.status}'!"
            )

        # Verifica a disponibilidade de vagas comparando matrículas ativas na turma com o seu limite máximo.
        if len(turma.matriculas_ativas) >= turma.vagas:
            raise ValueError(f"A turma '{turma.id_turma}' já atingiu o limite máximo de {turma.vagas} vagas!")

        # Extrai de forma rápida todas as turmas que o aluno já está cursando atualmente.
        disciplinas_ativas = {
            matricula.turma
            for matricula in aluno.historico
            if matricula.status == "Cursando"
        }

        # Extrai de forma rápida todos os cursos (disciplinas) nos quais o aluno já obteve aprovação.
        disciplinas_concluidas = {
            matricula.turma.curso
            for matricula in aluno.historico
            if matricula.status == "Aprovado"
        }

        # Impede que o aluno curse novamente uma disciplina que já está em andamento ou que já concluiu.
        if turma in disciplinas_ativas or turma.curso in disciplinas_concluidas:
            raise ValueError(f"O aluno '{aluno.nome}' já está cursando ou já foi aprovado em '{turma.curso.nome}'!")

        # Verifica se o aluno atingiu o teto de disciplinas simultâneas permitido pelo documento de configuração.
        if len(disciplinas_ativas) >= self.configuracao.max_turmas_por_aluno:
            raise ValueError(
                f"O aluno '{aluno.nome}' já atingiu o limite máximo de "
                f"{self.configuracao.max_turmas_por_aluno} turmas simultâneas!"
            )

        # Percorre a árvore de pré-requisitos para garantir que a ordem letiva está a ser respeitada.
        for pre_requisito in turma.curso.pre_requisitos:

            if pre_requisito not in disciplinas_concluidas:
                raise ValueError(
                    f"Pré-requisito não atendido! O aluno '{aluno.nome}' precisa ser aprovado "
                    f"em '{pre_requisito.nome}' antes de cursar '{turma.curso.nome}'."
                )

        # Avalia se há conflito de dias e horários entre a nova turma pretendida e as turmas atuais do aluno.
        if any(turma.verificar_choque_horario(disciplina) for disciplina in disciplinas_ativas):
            raise ValueError(f"Choque de horário detectado entre a turma '{turma.id_turma}' e uma disciplina em curso!")

        # Superadas todas as validações de negócio, instancia o vínculo oficial de matrícula.
        nova_matricula = Matricula(aluno, turma)

        # Adiciona a matrícula à lista geral do sistema para que seja persistida posteriormente.
        self._matriculas.append(nova_matricula)


    # READ: Métodos de Busca e Consulta de Entidades Ativas

    def buscar_aluno(self, identificador: str) -> Aluno | None:
        """Localiza e retorna um aluno ativo através do seu CPF ou número de Matrícula."""

        if not isinstance(identificador, str):
            raise TypeError("O identificador de busca do aluno (CPF ou matrícula) deve ser uma string!")

        identificador_limpo = identificador.strip()

        # Varre a coleção de alunos em memória buscando correspondência por CPF ou Matrícula.
        for aluno in self._alunos:

            if identificador_limpo == aluno.cpf or identificador_limpo == aluno.matricula:

                # Verifica se o registro não sofreu Soft Delete.
                if aluno.ativo:
                    return aluno

                print(f"Aviso: O aluno portador do identificador '{identificador_limpo}' encontra-se inativo!")
                return None

        print(f"Aviso: Matrícula ou CPF '{identificador_limpo}' não encontrado no sistema!")
        return None


    def buscar_turma(self, id_turma: str) -> Turma | None:
        """Localiza e retorna uma turma ativa através do seu identificador único."""

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser informado em formato de texto!")

        id_limpo = id_turma.strip()

        # Varre a lista de turmas verificando o identificador e o status de atividade (Soft Delete).
        for turma in self._turmas:

            if id_limpo == turma.id_turma:

                if turma.ativo:
                    return turma

                print(f"Aviso: A turma (ID: '{id_limpo}') encontra-se inativa!")
                return None

        print(f"Aviso: Turma (ID: '{id_limpo}') não encontrada no sistema!")
        return None


    def buscar_curso(self, codigo: str) -> Curso | None:
        """Localiza e retorna um curso ativo através do seu código único."""

        if not isinstance(codigo, str):
            raise TypeError("O código do curso deve ser informado em formato de texto!")

        codigo_limpo = codigo.strip().upper()

        # Varre o catálogo de disciplinas em busca do código correspondente.
        for curso in self._cursos:

            if codigo_limpo == curso.codigo:

                if curso.ativo:
                    return curso

                print(f"Aviso: O curso (Código: '{codigo_limpo}') encontra-se inativo!")
                return None

        print(f"Aviso: Curso (Código: '{codigo_limpo}') não encontrado no sistema!")
        return None


    def buscar_graduacao(self, codigo_mec: str) -> Graduacao | None:
        """Localiza e retorna uma graduação ativa através do seu código MEC."""

        if not isinstance(codigo_mec, str):
            raise TypeError("O código MEC da graduação deve ser informado em formato de texto!")

        codigo_limpo = re.sub(r"[^0-9]", "", codigo_mec)

        # Varre a lista de graduações cadastradas na instituição.
        for graduacao in self._graduacoes:

            if codigo_limpo == graduacao.codigo_mec:

                if graduacao.ativo:
                    return graduacao

                print(f"Aviso: A graduação (Código MEC: '{codigo_limpo}') encontra-se inativa!")
                return None

        print(f"Aviso: Graduação (Código MEC: '{codigo_limpo}') não encontrada no sistema!")
        return None


    # UPDATE: Métodos de Atualização Cadastral e Lançamentos Acadêmicos

    def atualizar_aluno(
        self,
        identificador: str,
        novo_nome: str | None = None,
        novo_telefone: str | None = None,
        novo_email: str | None = None
    ) -> None:
        """Atualiza parcialmente os dados cadastrais permitidos de um aluno ativo."""

        if not isinstance(identificador, str):
            raise TypeError("O identificador do aluno deve ser enviado em formato de texto!")

        if not isinstance(novo_nome, (str, type(None))):
            raise TypeError("O novo nome deve ser enviado em formato de texto ou None!")

        if not isinstance(novo_telefone, (str, type(None))):
            raise TypeError("O novo telefone deve ser enviado em formato de texto ou None!")

        if not isinstance(novo_email, (str, type(None))):
            raise TypeError("O novo e-mail deve ser enviado em formato de texto ou None!")

        aluno_encontrado = self.buscar_aluno(identificador)

        if aluno_encontrado is None:
            raise ValueError(f"Não foi possível atualizar: Aluno '{identificador}' não encontrado ou inativo!")

        # Atualiza apenas os campos efetivamente fornecidos pelo operador, passando pelos setters do domínio.
        if novo_nome is not None:
            aluno_encontrado.nome = novo_nome

        if novo_telefone is not None:
            aluno_encontrado.telefone = novo_telefone

        if novo_email is not None:
            aluno_encontrado.email = novo_email

        print(f"Dados do aluno '{aluno_encontrado.nome}' atualizados com sucesso!")


    def atualizar_turma(
        self,
        id_turma: str,
        novo_local: str | None = None,
        novas_vagas: int | None = None,
        novos_dias_horarios: dict | None = None
    ) -> None:
        """Atualiza local, capacidade de vagas ou grade de horários de uma turma ativa."""

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser enviado em formato de texto!")

        if not isinstance(novo_local, (str, type(None))):
            raise TypeError("O novo local deve ser enviado em formato de texto ou None!")

        if isinstance(novas_vagas, bool) or not isinstance(novas_vagas, (int, type(None))):
            raise TypeError("A nova quantidade de vagas deve ser um número inteiro ou None!")

        if not isinstance(novos_dias_horarios, (dict, type(None))):
            raise TypeError("Os novos dias e horários devem ser enviados em formato de dicionário ou None!")

        turma_encontrada = self.buscar_turma(id_turma)

        if turma_encontrada is None:
            raise ValueError(f"Não foi possível atualizar: Turma '{id_turma}' não encontrada ou inativa!")

        if novo_local is not None:
            turma_encontrada.local = novo_local

        if novas_vagas is not None:

            # Impede que a redução de capacidade deixe a turma com menos vagas do que alunos já inscritos.
            ocupacao_atual = len(turma_encontrada.matriculas_ativas)

            if novas_vagas < ocupacao_atual:
                raise ValueError(
                    f"Operação negada! O novo limite de vagas ({novas_vagas}) não pode ser menor "
                    f"que a quantidade de alunos atualmente matriculados ({ocupacao_atual})."
                )

            turma_encontrada.vagas = novas_vagas

        if novos_dias_horarios is not None:

            if not novos_dias_horarios:
                raise ValueError("O dicionário de novos dias e horários não pode estar vazio!")

            # Verifica se a mudança de horário causará conflito na grade de algum aluno já matriculado na turma.
            for matricula_ativa in turma_encontrada.matriculas_ativas:

                for outra_matricula in matricula_ativa.aluno.historico:

                    # Compara apenas com outras disciplinas que o aluno está cursando em paralelo.
                    if outra_matricula.turma != turma_encontrada and outra_matricula.status == "Cursando":

                        horarios_comuns = outra_matricula.turma.dias_horarios.items() & novos_dias_horarios.items()

                        if horarios_comuns:
                            raise ValueError(
                                f"Operação negada! O novo horário gera choque para o aluno "
                                f"'{matricula_ativa.aluno.nome}' com a turma '{outra_matricula.turma.id_turma}'."
                            )

            turma_encontrada.dias_horarios = novos_dias_horarios

        print(f"Dados da turma '{turma_encontrada.id_turma}' atualizados com sucesso!")


    def atualizar_curso(
        self,
        codigo: str,
        novo_nome: str | None = None,
        nova_carga_horaria: int | None = None,
        nova_ementa: str | None = None
    ) -> None:
        """Atualiza o nome, a carga horária ou a ementa de um curso ativo (respeitando as regras de dependência)."""

        if not isinstance(codigo, str):
            raise TypeError("O código do curso deve ser enviado em formato de texto!")

        if not isinstance(novo_nome, (str, type(None))):
            raise TypeError("O novo nome do curso deve ser enviado em formato de texto ou None!")

        if isinstance(nova_carga_horaria, bool) or not isinstance(nova_carga_horaria, (int, type(None))):
            raise TypeError("A nova carga horária deve ser um número inteiro ou None!")

        if not isinstance(nova_ementa, (str, type(None))):
            raise TypeError("A nova ementa deve ser enviada em formato de texto ou None!")

        curso_encontrado = self.buscar_curso(codigo)

        if curso_encontrado is None:
            raise ValueError(f"Não foi possível atualizar: Curso '{codigo}' não encontrado ou inativo!")

        if novo_nome is not None:
            curso_encontrado.nome = novo_nome

        # Regra de negócio: Carga horária não pode ser atualizada isoladamente sem a ementa.
        if nova_carga_horaria is not None and nova_ementa is None:
            raise ValueError("Operação negada! Não é permitido atualizar a carga horária sem atualizar a ementa do curso simultaneamente.")

        # Atualiza apenas a ementa caso fornecida isoladamente.
        if nova_ementa is not None and nova_carga_horaria is None:
            curso_encontrado.ementa = nova_ementa

        # Atualiza ambos caso a carga horária seja informada (com a ementa obrigatória).
        if nova_carga_horaria is not None and nova_ementa is not None:
            curso_encontrado.alterar_carga_horaria(nova_carga_horaria, nova_ementa)

        print(f"Dados do curso '{curso_encontrado.nome}' atualizados com sucesso!")


    def atualizar_graduacao(
        self,
        codigo_mec: str,
        novo_nome: str | None = None,
        nova_qtd_semestres: int | None = None
    ) -> None:
        """Atualiza o nome ou a duração em semestres de uma graduação ativa."""

        if not isinstance(codigo_mec, str):
            raise TypeError("O código MEC deve ser enviado em formato de texto!")

        if not isinstance(novo_nome, (str, type(None))):
            raise TypeError("O novo nome da graduação deve ser enviado em formato de texto ou None!")

        if isinstance(nova_qtd_semestres, bool) or not isinstance(nova_qtd_semestres, (int, type(None))):
            raise TypeError("A nova quantidade de semestres deve ser um número inteiro ou None!")

        graduacao_encontrada = self.buscar_graduacao(codigo_mec)

        if graduacao_encontrada is None:
            raise ValueError(f"Não foi possível atualizar: Graduação '{codigo_mec}' não encontrada ou inativa!")

        if novo_nome is not None:
            graduacao_encontrada.nome = novo_nome

        if nova_qtd_semestres is not None:
            graduacao_encontrada.qtd_semestres = nova_qtd_semestres

        print(f"Dados da graduação '{graduacao_encontrada.nome}' atualizados com sucesso!")


    def lancar_nota_aluno(
        self, identificador_aluno: str, id_turma: str, nome_avaliacao: str, nota: float
    ) -> None:
        """Localiza a matrícula ativa do aluno na turma especificada e registra a nota da avaliação."""

        if not isinstance(identificador_aluno, str):
            raise TypeError("O identificador do aluno deve ser enviado em formato de texto!")

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser enviado em formato de texto!")

        aluno_encontrado = self.buscar_aluno(identificador_aluno)

        if aluno_encontrado is None:
            raise ValueError(f"Lançamento negado: Aluno '{identificador_aluno}' não encontrado ou inativo!")

        turma_encontrada = self.buscar_turma(id_turma)

        if turma_encontrada is None:
            raise ValueError(f"Lançamento negado: Turma '{id_turma}' não encontrada ou inativa!")

        # Procura o vínculo exato entre o aluno e a turma dentro do histórico acadêmico.
        for matricula in aluno_encontrado.historico:

            if matricula.turma == turma_encontrada:

                matricula.lancar_nota(nome_avaliacao, nota)
                print("Nota lançada com sucesso!")
                return

        raise ValueError(
            f"O aluno '{aluno_encontrado.nome}' não possui matrícula registrada na turma '{turma_encontrada.id_turma}'!"
        )


    def lancar_frequencia_aluno(self, identificador_aluno: str, id_turma: str, horas: int) -> None:
        """Localiza a matrícula do aluno na turma e contabiliza as horas-aula assistidas."""

        if not isinstance(identificador_aluno, str):
            raise TypeError("O identificador do aluno deve ser enviado em formato de texto!")

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser enviado em formato de texto!")

        aluno_encontrado = self.buscar_aluno(identificador_aluno)

        if aluno_encontrado is None:
            raise ValueError(f"Lançamento negado: Aluno '{identificador_aluno}' não encontrado ou inativo!")

        turma_encontrada = self.buscar_turma(id_turma)

        if turma_encontrada is None:
            raise ValueError(f"Lançamento negado: Turma '{id_turma}' não encontrada ou inativa!")

        # Procura o vínculo exato entre o aluno e a turma dentro do histórico acadêmico.
        for matricula in aluno_encontrado.historico:

            if matricula.turma == turma_encontrada:

                matricula.lancar_frequencia(horas)
                print("Frequência lançada com sucesso!")
                return

        raise ValueError(
            f"O aluno '{aluno_encontrado.nome}' não possui matrícula registrada na turma '{turma_encontrada.id_turma}'!"
        )


    def consolidar_situacao_turma(self, id_turma: str) -> None:
        """Avalia notas e frequências de todos os alunos cursando a turma para definir aprovação ou reprovação."""

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser enviado em formato de texto!")

        turma_encontrada = self.buscar_turma(id_turma)

        if turma_encontrada is None:
            raise ValueError(f"Consolidação negada: Turma '{id_turma}' não encontrada ou inativa!")

        # Atualiza a situação apenas das matrículas que ainda não foram trancadas.
        for matricula in turma_encontrada.matriculas_ativas:

            if matricula.status != "Trancada":
                matricula.atualizar_situacao(self.configuracao)


    # DELETE (Soft Delete): Métodos de Inativação Lógica e Encerramento

    def inativar_aluno(self, identificador_aluno: str) -> None:
        """Realiza o Soft Delete de um aluno, desde que não possua disciplinas em andamento."""

        if not isinstance(identificador_aluno, str):
            raise TypeError("O identificador do aluno deve ser enviado em formato de texto!")

        aluno_encontrado = self.buscar_aluno(identificador_aluno)

        if aluno_encontrado is None:
            raise ValueError(f"Inativação negada: Aluno '{identificador_aluno}' não encontrado ou já inativo!")

        # Impede a desativação caso o aluno ainda esteja cursando alguma disciplina ativa no semestre.
        if any(matricula.status == "Cursando" for matricula in aluno_encontrado.historico):
            raise ValueError(
                f"Operação negada! O aluno '{aluno_encontrado.nome}' possui disciplinas em andamento ('Cursando'). "
                f"Realize o trancamento ou encerramento antes de inativar o registo."
            )

        aluno_encontrado.ativo = False
        print(f"Aluno '{aluno_encontrado.nome}' inativado com sucesso!")


    def inativar_curso(self, codigo: str) -> None:
        """Realiza o Soft Delete de um curso, desde que não possua turmas abertas."""

        if not isinstance(codigo, str):
            raise TypeError("O código do curso deve ser enviado em formato de texto!")

        curso_encontrado = self.buscar_curso(codigo)

        if curso_encontrado is None:
            raise ValueError(f"Inativação negada: Curso '{codigo}' não encontrado ou já inativo!")

        # Bloqueia a desativação se houver qualquer turma ativa e aberta ofertando esta disciplina.
        if any(turma.status == "Aberta" and turma.ativo for turma in curso_encontrado.turmas_ofertadas):
            raise ValueError(
                f"Operação negada! O curso '{curso_encontrado.nome}' possui turmas abertas em andamento."
            )

        curso_encontrado.ativo = False
        print(f"Curso '{curso_encontrado.nome}' inativado com sucesso!")


    def inativar_graduacao(self, codigo_mec: str) -> None:
        """Realiza o Soft Delete de uma graduação, desde que não possua disciplinas ativas vinculadas."""

        if not isinstance(codigo_mec, str):
            raise TypeError("O código MEC deve ser enviado em formato de texto!")

        graduacao_encontrada = self.buscar_graduacao(codigo_mec)

        if graduacao_encontrada is None:
            raise ValueError(f"Inativação negada: Graduação '{codigo_mec}' não encontrada ou já inativa!")

        # Bloqueia a inativação caso a grade curricular ainda contenha cursos ativos.
        if any(curso.ativo for curso in graduacao_encontrada.grade_curricular):
            raise ValueError(
                f"Operação negada! A graduação '{graduacao_encontrada.nome}' ainda possui disciplinas ativas na grade."
            )

        graduacao_encontrada.ativo = False
        print(f"Graduação '{graduacao_encontrada.nome}' inativada com sucesso!")


    def inativar_turma(self, id_turma: str) -> None:
        """Realiza o Soft Delete de uma oferta de turma caso não existam alunos cursando."""

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser enviado em formato de texto!")

        turma_encontrada = self.buscar_turma(id_turma)

        if turma_encontrada is None:
            raise ValueError(f"Inativação negada: Turma '{id_turma}' não encontrada ou já inativa!")

        if any(matricula.status == "Cursando" for matricula in turma_encontrada.matriculas_ativas):
            raise ValueError(
                f"Operação negada! A turma '{turma_encontrada.id_turma}' possui alunos com matrícula em andamento."
            )

        turma_encontrada.ativo = False
        print(f"Turma '{turma_encontrada.id_turma}' inativada com sucesso!")


    def encerrar_turma(self, id_turma: str) -> None:
        """Consolida as notas/frequências de todos os inscritos e fecha a oferta da turma no semestre."""

        if not isinstance(id_turma, str):
            raise TypeError("O ID da turma deve ser enviado em formato de texto!")

        turma_encontrada = self.buscar_turma(id_turma)

        if turma_encontrada is None:
            raise ValueError(f"Encerramento negado: Turma '{id_turma}' não encontrada ou inativa!")

        # Verifica o quórum mínimo antes de consolidar as situações para não alterar status em caso de falha.
        if len(turma_encontrada.matriculas_ativas) < 5:
            raise ValueError(
                f"A turma '{turma_encontrada.id_turma}' não atingiu o quórum mínimo de 5 alunos "
                f"(Atuais: {len(turma_encontrada.matriculas_ativas)})!"
            )

        # Consolida aprovações e reprovações e, em seguida, fecha a turma.
        self.consolidar_situacao_turma(id_turma)
        turma_encontrada.fechar_turma()
        print(f"Turma '{turma_encontrada.id_turma}' consolidada e encerrada com sucesso!")


    # Métodos de Persistência (Ponte entre Memória e Disco)

    def salvar_estado(self) -> None:
        """Aciona os 5 repositórios para serializar as listas da memória e gravá-las no disco em formato JSON."""

        self.__repo_graduacao.salvar(self._graduacoes)
        self.__repo_curso.salvar(self._cursos)
        self.__repo_turma.salvar(self._turmas)
        self.__repo_aluno.salvar(self._alunos)
        self.__repo_matricula.salvar(self._matriculas)


    def carregar_estado(self) -> None:
        """
        Aciona os 5 repositórios para ler os JSONs no disco e recriar as entidades em memória.
        A ordem de hidratação é rigorosamente mantida para resolver as dependências das Chaves Estrangeiras.
        """

        self._graduacoes = self.__repo_graduacao.carregar()
        self._cursos = self.__repo_curso.carregar(self._graduacoes)
        self._turmas = self.__repo_turma.carregar(self._cursos)
        self._alunos = self.__repo_aluno.carregar(self._graduacoes)
        self._matriculas = self.__repo_matricula.carregar(self._alunos, self._turmas)

        # -------------------------------------------------------------------------
        # READ: Métodos de Geração de Relatórios Acadêmicos
        # -------------------------------------------------------------------------

        def gerar_relatorio_alunos_turma(self, id_turma: str) -> None:
            """Mostra vagas ocupadas em relação às vagas totais de uma determinada turma, listando os inscritos."""

            if not isinstance(id_turma, str):
                raise TypeError("O ID da turma deve ser enviado em formato de texto!")

            turma_encontrada = self.buscar_turma(id_turma)

            if turma_encontrada is None:
                raise ValueError(f"Relatório negado: Turma '{id_turma}' não encontrada ou inativa!")

            capacidade_total = turma_encontrada.vagas
            vagas_ocupadas = len(turma_encontrada.matriculas_ativas)

            # Medida de segurança contra divisão por zero.
            porcentagem_lotacao = (vagas_ocupadas / capacidade_total) * 100 if capacidade_total > 0 else 0

            # Impressão de Cabeçalho Estruturado.
            print("\n" + "=" * 50)
            print(f" RELATÓRIO DE OCUPAÇÃO DA TURMA: {turma_encontrada.id_turma}")
            print(f" Curso: {turma_encontrada.curso.nome}")
            print(f" Ocupação: {vagas_ocupadas} de {capacidade_total} vagas ({porcentagem_lotacao:.1f}%)")
            print("=" * 50)

            if not turma_encontrada.matriculas_ativas:
                print(" Nenhum aluno matriculado nesta turma até o momento.")
            else:
                print(" ALUNO(A)\t\tMATRÍCULA\tSTATUS")
                print("-" * 50)

                # Varre e exibe os alunos garantindo alinhamento visual em tela.
                for matricula in turma_encontrada.matriculas_ativas:
                    print(f" {matricula.aluno.nome[:15]:<15}\t{matricula.aluno.matricula}\t{matricula.status}")

            print("=" * 50 + "\n")

        def gerar_relatorio_taxa_aprovacao(self) -> None:
            """Exibe a porcentagem de aprovação global e detalhada por graduação na instituição."""

            # Filtra as matrículas ativas desconsiderando quem ainda está cursando ou trancou.
            total_avaliados = [matricula for matricula in self.matriculas if
                               matricula.status not in ["Cursando", "Trancada"]]

            # Filtra, a partir dos avaliados, os que lograram êxito.
            total_aprovados = [matricula for matricula in total_avaliados if matricula.status == "Aprovado"]

            print("\n" + "=" * 50)
            print(" RELATÓRIO INSTITUCIONAL DE TAXA DE APROVAÇÃO")
            print("=" * 50)

            # Prevenção contra Divisão por Zero em cenários onde não há consolidações ainda.
            if not total_avaliados:
                print(" Aviso: Não há matrículas consolidadas para gerar este relatório.")
                print("=" * 50 + "\n")
                return

            taxa_aprovacao_global = (len(total_aprovados) / len(total_avaliados)) * 100

            print(f" Total de Avaliados Institucionais: {len(total_avaliados)}")
            print(f" Taxa de Aprovação Global: {taxa_aprovacao_global:.2f}%")
            print("-" * 50)

            # Gera métricas isoladas para cada graduação ativa no sistema.
            for graduacao in self.graduacoes:

                # Avaliados específicos desta graduação.
                avaliados_grad = [mat for mat in total_avaliados if
                                  mat.aluno.graduacao.codigo_mec == graduacao.codigo_mec]

                if avaliados_grad:
                    aprovados_grad = [mat for mat in avaliados_grad if mat.status == "Aprovado"]

                    taxa_grad = (len(aprovados_grad) / len(avaliados_grad)) * 100

                    print(f" [ {graduacao.nome} ]")
                    print(f"   Avaliados: {len(avaliados_grad)} | Aprovação: {taxa_grad:.2f}%")

            print("=" * 50 + "\n")

        def gerar_relatorio_distribuicao_notas(self, id_turma: str) -> None:
            """Calcula as métricas estatísticas de média, mediana e desvio padrão das notas de uma turma."""

            if not isinstance(id_turma, str):
                raise TypeError("O ID da turma deve ser enviado em formato de texto!")

            turma_encontrada = self.buscar_turma(id_turma)

            if turma_encontrada is None:
                raise ValueError(f"Relatório negado: Turma '{id_turma}' não encontrada ou inativa!")

            # Extrai apenas os números finais de notas lançadas, desconsiderando os 'None'.
            notas = [matricula.notas["MF"] for matricula in turma_encontrada.matriculas_ativas if
                     matricula.notas["MF"] is not None]

            print("\n" + "=" * 50)
            print(f" DISTRIBUIÇÃO ESTATÍSTICA DE NOTAS: {turma_encontrada.id_turma}")
            print(f" Curso: {turma_encontrada.curso.nome}")
            print("=" * 50)

            # O cálculo de desvio padrão exige no mínimo duas amostras preenchidas.
            if len(notas) < 2:
                print(" Aviso: São necessários pelo menos 2 alunos com notas fechadas")
                print("        para calcular as estatísticas de desvio padrão.")
                print("=" * 50 + "\n")
                return

            # Aciona os motores de cálculo da biblioteca Statistics.
            media = statistics.mean(notas)
            mediana = statistics.median(notas)
            desvio_padrao = statistics.stdev(notas)

            print(f" Amostra Consolidada: {len(notas)} alunos")
            print("-" * 50)
            print(f" Média Aritmética: {float(media):.2f}")
            print(f" Mediana: {float(mediana):.2f}")
            print(f" Desvio Padrão: {float(desvio_padrao):.2f}")
            print("=" * 50 + "\n")

        def gerar_relatorio_alunos_risco(self) -> None:
            """Mapeia alunos ativos no semestre cujas parciais não atendem aos parâmetros mínimos de aprovação."""

            # Seleciona apenas os alunos ativamente engajados (status 'Cursando').
            matriculas_ativas = [matricula for matricula in self.matriculas if matricula.status == "Cursando"]

            # Puxa os parâmetros globais estipulados no arquivo 'settings.json'.
            nota_minima = self.configuracao.nota_minima_aprovacao
            frequencia_minima = self.configuracao.frequencia_minima

            # Verifica se o aluno já fez as provas (AV1 e AV2 não nulas) mas a média final continua abaixo do corte.
            risco_notas = [
                matricula for matricula in matriculas_ativas
                if matricula.notas["MF"] is not None and matricula.notas["MF"] < nota_minima
            ]

            # A propriedade matricula.frequencia já devolve o valor percentual (0 a 100).
            risco_faltas = [
                matricula for matricula in matriculas_ativas
                if matricula.frequencia < frequencia_minima
            ]

            print("\n" + "=" * 60)
            print(" ALERTA INSTITUCIONAL: ALUNOS EM ZONA DE RISCO")
            print("=" * 60)

            print(f"\n [ RISCO POR NOTA ] (Abaixo de {nota_minima:.1f})")
            if not risco_notas:
                print("   Nenhum aluno em risco por nota.")
            else:
                for matricula in risco_notas:
                    print(
                        f"   {matricula.aluno.matricula} | {matricula.aluno.nome[:15]:<15} | Turma: {matricula.turma.id_turma}")

            print(f"\n [ RISCO POR FALTA ] (Abaixo de {frequencia_minima:.1f}%)")
            if not risco_faltas:
                print("   Nenhum aluno em risco por frequência.")
            else:
                for matricula in risco_faltas:
                    print(
                        f"   {matricula.aluno.matricula} | {matricula.aluno.nome[:15]:<15} | Turma: {matricula.turma.id_turma}")

            print("\n" + "=" * 60 + "\n")

        def gerar_relatorio_top_n(self, periodo: str) -> None:
            """Agrupa e calcula a média semestral (CR temporário) dos alunos, retornando os 'N' melhores do período."""

            if not isinstance(periodo, str):
                raise TypeError("O período de referência deve ser informado em formato de texto!")

            # Isola as matrículas que foram concluídas com sucesso no período requisitado.
            aprovados_periodo = [
                matricula for matricula in self.matriculas
                if matricula.turma.periodo == periodo and matricula.status == "Aprovado"
            ]

            print("\n" + "=" * 50)
            print(f" RANKING DE EXCELÊNCIA (TOP {self.configuracao.top_n_alunos}) - PERÍODO {periodo}")
            print("=" * 50)

            if not aprovados_periodo:
                print(f" Nenhuma aprovação consolidada encontrada para '{periodo}'.")
                print("=" * 50 + "\n")
                return

            top_alunos = []
            matriculas_processadas = []

            # Agrupa o histórico do aluno e calcula a média das suas aprovações no semestre em questão.
            for matricula in aprovados_periodo:

                aluno_atual = matricula.aluno

                # Bloqueio para evitar processar o mesmo aluno múltiplas vezes.
                if aluno_atual.matricula in matriculas_processadas:
                    continue

                # Extrai todas as aprovações DESTE aluno NESTE período.
                matriculas_aluno_periodo = [
                    m for m in aprovados_periodo
                    if m.aluno.matricula == aluno_atual.matricula
                ]

                # Soma as médias finais (MF) e divide pelo número de matérias feitas.
                media_aluno_periodo = sum(m.notas["MF"] for m in matriculas_aluno_periodo) / len(
                    matriculas_aluno_periodo)

                top_alunos.append((aluno_atual.nome, media_aluno_periodo))
                matriculas_processadas.append(aluno_atual.matricula)

            # Ordena a lista pelas médias (índice 1 da tupla) em ordem decrescente (do maior para o menor).
            top_alunos.sort(key=lambda x: x[1], reverse=True)

            # Fatia a lista limitando a quantidade de alunos ao estabelecido nas configurações da Instituição.
            top_alunos = top_alunos[:self.configuracao.top_n_alunos]

            for indice, (nome, media) in enumerate(top_alunos, start=1):
                print(f" {indice}º LUGAR: {nome[:25]:<25} | Média: {media:.2f}")

            print("=" * 50 + "\n")