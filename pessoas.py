import re

class Pessoa:
    """
    Classe base que concentra os dados de identificação comuns a qualquer 
    pessoa na instituição (nome, CPF, telefone e e-mail).
    """

    # Construção da classe
    def __init__(self, nome: str, cpf: str, telefone: str, email: str) -> None:
        self.nome = nome
        self.cpf = cpf
        self._telefone = telefone
        self._email = email

    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def nome(self):
        return self._nome

    # Transforma a atribuição num Setter com validação obrigatória
    @nome.setter
    def nome(self, novo_nome):

        # Retira qualquer qualquer coisas que não seja letras de A a Z, 
        # letras acentuadas (do À ao ÿ) e espaços.
        novo_nome = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', novo_nome)

        # Realiza verificação de tamanho mínimo
        if len(novo_nome) > 6:
            self._nome = novo_nome

       # Notifica erro se o nome não cumprir requisitos
        else:
            raise ValueError("Nome inválido!")
        

    def __validar_cpf(self, cpf_digitado: str) -> bool:
        """
        Função responsável por realizar a "limpeza" e validação do CPF digitado,
        removendo qualquer coisa que não seja um dígito (0-9), impedindo CPFs como "00000000000",
        verificando o tamanho do CPF digitado e executando verificação matemática de dígitos verificadores.
        """

        # Retira qualquer qualquer coisas que não sejam dígitos (0-9)
        cpf_limpo = re.sub(r'[^0-9]', '', cpf_digitado)

        # Barra CPFs como "00000000000", "11111111111", "22222222222", etc.
        if len(set(cpf_limpo)) == 1:
            return False

        # Verifica o tamanho exato do CPF digitado
        elif len(cpf_limpo) != 11:
            return False

        # Validação matemática do 1º dígito verificador
        verificacao_cpf = int(cpf_limpo[0:9])
        dig_veri_1 = [verificacao_cpf*i for i in range(10, 1, -1)]
        dig_veri_1 = (sum(dig_veri_1) * 10) % 11

        if dig_veri_1 == 10 or dig_veri_1 == 11:
            dig_veri_1 = 0

        if dig_veri_1 != cpf_limpo[9]:
            return False

        
        # Validação matemática do 1º dígito verificador
        verificacao_cpf = int(cpf_limpo[0:10])
        dig_veri_2 = [verificacao_cpf*i for i in range(11, 1, -1)]
        dig_veri_2 = (sum(dig_veri_2) * 10) % 11

        if dig_veri_2 == 10 or dig_veri_2 == 11:
            dig_veri_2 = 0

        if dig_veri_2 != cpf_limpo[10]:
            return False

        # Valida o CPF caso tenha passado por todas as verificações
        return True
        

    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def cpf(self):
        return self._cpf

    # Transforma a atribuição num Setter com validação obrigatória
    @cpf.setter
    def cpf(self, novo_cpf):

        # Chama a função d validação de CPF e já realiza a atribuição com o CPF "limpo"
        if self.__validar_cpf(novo_cpf):
            self._cpf = re.sub(r'[^0-9]', '', novo_cpf)        

        # Notifica erro se o CPF não cumprir requisitos
        else:
            raise ValueError("CPF inválido!")
    



    

    

    