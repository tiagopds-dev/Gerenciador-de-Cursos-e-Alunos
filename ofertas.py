from datetime import date 

class Oferta:
    """
    Classe base que abstrai o conceito de algo sendo oferecido no tempo e espaço, 
    contendo o período letivo, horários, local e limite de vagas.
    """

    # Construção da classe
    def __init__(self, periodo: str, dias_horarios: dict, vagas: int, local: str) -> None:
        self.periodo = periodo
        self.dias_horarios = dias_horarios
        self.vagas = vagas
        self.local = local

    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def periodo(self):
        return self._periodo

    
    # Transforma a atribuição num Setter com validação obrigatória
    @periodo.setter
    def periodo(self, novo_local):

        # Valida tamanho exato do formato definido para período
        if len(novo_local) != 6:
            raise ValueError("Periodo inválido!")

        # Valida o ano do período fornecido se encontra dentro do intervalo aceitável de anos
        datas_validas = [data for data in range((date.today().year - 1), (date.today().year) + 2)]
        if int(novo_local[0:4]) not in datas_validas:
            raise ValueError("Periodo inválido!")

        # Valida se o "semestre" fornecido no período está de acordo com o padrão
        if novo_local[4:6] != ".1" and novo_local[4:6] != ".2":
            raise ValueError("Periodo inválido!")

        # Segue com a atribuição se todas as verificações foram atendidas
        self._periodo = novo_local

    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def dias_horarios(self):
        return self._dias_horarios


    # Transforma a atribuição num Setter com validação obrigatória
    @dias_horarios.setter
    def dias_horarios(self, novo_dias_horarios):
        
        # Garante que a atribuição será feita apenas se o dicionário não estiver vazio
        if novo_dias_horarios:
            self._dias_horarios = novo_dias_horarios

        # Lança exceção, caso contrário
        else:
            raise ValueError("Dias e horários não fornecidos!")

    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def vagas(self):
        return self._vagas

    # Transforma a atribuição num Setter com validação obrigatória
    @vagas.setter
    def vagas(self, novas_vagas):

        # Garante que a atribuição será feita apenas se a quantidade de vagas for positiva
        if novas_vagas > 0:
            self._vagas = novas_vagas

        # Lança exceção, caso contrário
        else:
            raise ValueError("Número de vagas inválidas!")


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def local(self):
        return self._local

    
    # Transforma a atribuição num Setter com validação obrigatória
    @local.setter
    def local(self, novo_local):

        # Valida tamanho exato do formato definido para período
        if len(novo_local) < 4:
            raise ValueError("Periodo inválido!")

        # Segue com a atribuição se todas as verificações foram atendidas
        self._periodo = novo_local
        