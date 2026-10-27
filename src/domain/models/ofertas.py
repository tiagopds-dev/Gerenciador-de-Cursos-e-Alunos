from datetime import date


# Construção da classe.
class Oferta:
    """
    Classe base que abstrai o conceito de algo sendo oferecido no tempo e espaço,
    contendo o período letivo, horários, local e limite de vagas.
    """


    def __init__(self, periodo: str, dias_horarios: dict, vagas: int, local: str) -> None:

        self.periodo = periodo

        self.dias_horarios = dias_horarios

        self.vagas = vagas

        self.local = local


    @property
    def periodo(self):
        return self._periodo


    @periodo.setter
    def periodo(self, novo_periodo: str):

        # Valida o tipo de dado para evitar falhas na etapa de verificação do ano.
        if not isinstance(novo_periodo, str):
            raise TypeError("O período deve ser enviado em formato de texto (ex: '2026.1')!")

        # Valida o tamanho exato do formato definido para período.
        if len(novo_periodo) != 6:
            raise ValueError(
                f"O formato do período é inválido! "
                f"Esperado 6 caracteres ('AAAA.S'), mas recebeu {len(novo_periodo)} ('{novo_periodo}')."
            )

        # Garante que os 4 primeiros caracteres são numéricos antes de tentar converter para inteiro.
        ano_str = novo_periodo[0:4]

        if not ano_str.isdigit():
            raise ValueError(f"O ano do período deve conter apenas números! Valor recebido: '{ano_str}'.")

        # Valida se o ano do período fornecido se encontra dentro do intervalo aceitável.
        ano_atual = date.today().year

        datas_validas = [ano_atual - 1, ano_atual, ano_atual + 1]

        if int(ano_str) not in datas_validas:
            raise ValueError(
                f"O ano do período ('{ano_str}') está fora do limite permitido! "
                f"Anos válidos: {datas_validas[0]}, {datas_validas[1]} ou {datas_validas[2]}."
            )

        # Valida se o semestre fornecido no período está conforme o padrão.
        semestre_str = novo_periodo[4:6]

        if semestre_str not in [".1", ".2"]:
            raise ValueError(
                f"O identificador de semestre ('{semestre_str}') é inválido! Utilize obrigatoriamente '.1' ou '.2'."
            )

        # Segue com a atribuição se todas as verificações foram atendidas.
        self._periodo = novo_periodo


    @property
    def dias_horarios(self):
        return self._dias_horarios


    @dias_horarios.setter
    def dias_horarios(self, novo_dias_horarios: dict):

        if not isinstance(novo_dias_horarios, dict):
            raise TypeError("Os dias e horários devem ser enviados no formato de dicionário!")

        # Garante que a atribuição será feita apenas se o dicionário não estiver vazio.
        if not novo_dias_horarios:
            raise ValueError("O dicionário de dias e horários não pode estar vazio!")

        self._dias_horarios = novo_dias_horarios


    @property
    def vagas(self):
        return self._vagas


    @vagas.setter
    def vagas(self, novas_vagas: int):

        if not isinstance(novas_vagas, int) or isinstance(novas_vagas, bool):
            raise TypeError("O número de vagas deve ser um número inteiro!")

        # Garante que a atribuição será feita apenas se a quantidade de vagas for positiva.
        if novas_vagas <= 0:
            raise ValueError(f"O número de vagas deve ser maior que zero! Valor recebido: {novas_vagas}.")

        self._vagas = novas_vagas


    @property
    def local(self):
        return self._local


    @local.setter
    def local(self, novo_local: str):

        if not isinstance(novo_local, str):
            raise TypeError("O local da oferta deve ser enviado em formato de texto!")

        # Valida o tamanho mínimo do formato definido para local.
        if not novo_local.strip() or len(novo_local) < 4:
            raise ValueError("O nome do local deve conter pelo menos 4 letras válidas!")

        # Segue com a atribuição se todas as verificações foram atendidas.
        self._local = novo_local