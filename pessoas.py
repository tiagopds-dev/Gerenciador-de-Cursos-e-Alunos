import re

class Pessoa:
    """
    Classe base que concentra os dados de identificação comuns a qualquer 
    pessoa na instituição (nome, CPF, telefone e e-mail).
    """

    # Construção da classe
    def __init__(self, nome: str, cpf: str, telefone: str, email: str) -> None:
        
        # Inicializa o nome da pessoa (passando pela validação do setter)
        self.nome = nome
        
        # Inicializa o CPF da pessoa (passando pela validação geral do setter e específica do método validar_cpf)
        self.cpf = cpf

        # Inicializa o telefone da pessoa (passando pela validação do setter)
        self.telefone = telefone
        self.email = email


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def nome(self):
        return self._nome


    # Transforma a atribuição num Setter com validação obrigatória
    @nome.setter
    def nome(self, novo_nome):

        # Valida tamanho exato do argumento passado para nome e garante que seja uma string
        if not isinstance(novo_nome, str) or not novo_nome or len(novo_nome) < 6:
            raise Exception("Nome inválido!")

        # Retira qualquer qualquer coisas que não seja letras de A a Z, letras acentuadas (do À ao ÿ) e espaços
        # Formata o nome, deixando a primeira letra de cada palavra maiúscula
        novo_nome = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', novo_nome).title()

        # Caso o critério seja atendido, faz atribução segura
        self._nome = novo_nome
        

    def __validar_cpf(self, cpf_digitado: str) -> bool:
        """
        Função responsável por realizar a "limpeza" e validação do CPF digitado,
        removendo qualquer coisa que não seja um dígito (0-9), impedindo CPFs como "00000000000",
        verificando o tamanho do CPF digitado e executando verificação matemática de dígitos verificadores.
        """

        # Retira quaisquer coisas que não sejam dígitos (0-9)
        cpf_limpo = re.sub(r'[^0-9]', '', cpf_digitado)

        # Barra CPFs como "00000000000", "11111111111", "22222222222", etc.
        if len(set(cpf_limpo)) == 1:
            return False

        # Verifica o tamanho exato do CPF digitado
        if len(cpf_limpo) != 11:
            return False

        # Validação matemática do 1º dígito verificador
        dig_veri_1 = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        dig_veri_1 = (dig_veri_1) * 10 % 11

        if dig_veri_1 == 10 or dig_veri_1 == 11:
            dig_veri_1 = 0

        if str(dig_veri_1) != (cpf_limpo[9]):
            return False

        
        # Validação matemática do 1º dígito verificador
        dig_veri_2 = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        dig_veri_2 = (dig_veri_2 * 10) % 11

        if dig_veri_2 == 10 or dig_veri_2 == 11:
            dig_veri_2 = 0

        if str(dig_veri_2) != cpf_limpo[10]:
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

        # Valida tamanho exato do argumento passado para CPF e garante que seja uma string
        if not isinstance(novo_cpf, str) or not novo_cpf or len(novo_cpf) < 11:
            raise Exception("CPF inválido!")        

        # Chama a função de validação de CPF e já realiza a atribuição com o CPF "limpo"
        if self.__validar_cpf(novo_cpf):
            self._cpf = re.sub(r'[^0-9]', '', novo_cpf)        

        # Notifica erro se o CPF não cumprir requisitos
        else:
            raise Exception("CPF inválido!")


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def telefone(self):
        return self._telefone


    # Transforma a atribuição num Setter com validação obrigatória
    @telefone.setter
    def telefone(self, novo_telefone):

        # Retira quaisquer coisas que não sejam dígitos (0-9)
        novo_telefone = re.sub(r'[^0-9]', '', novo_telefone)

        # Realiza verificação de tamanho mínimo
        if len(novo_telefone) == 11:
            self._telefone = novo_telefone

       # Notifica erro se o nome não cumprir requisitos
        else:
            raise ValueError("Telefone inválido!")


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def email(self):
        return self._email


    # Transforma a atribuição num Setter com validação obrigatória
    @email.setter
    def email(self, novo_email):

        # Realiza verificação de formatação do e-mail
        if ".com" in novo_email and "@" in novo_email:
            self._email = novo_email

       # Notifica erro se o email não cumprir requisitos
        else:
            raise ValueError("Email inválido!")