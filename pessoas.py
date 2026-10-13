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

        # Inicializa o e-mail da pessoa (passando pela validação do setter)
        self.email = email


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def nome(self):
        return self._nome


    # Transforma a atribuição num Setter com validação obrigatória
    @nome.setter
    def nome(self, novo_nome):

        # Valida o tipo de dado para garantir que o argumento passado seja uma string
        if not isinstance(novo_nome, str):
            raise TypeError("O nome deve ser enviado em formato de texto!")

        # Retira quaisquer coisas que não sejam letras de A a Z, letras acentuadas (do À ao ÿ) e espaços
        # Formata o nome, deixando a primeira letra de cada palavra maiúscula e removendo espaços nas pontas
        novo_nome_limpo = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', novo_nome).title().strip()

        # Valida o tamanho mínimo da string após a higienização 
        if len(novo_nome_limpo) < 6:
            raise ValueError("O nome deve conter pelo menos 6 caracteres válidos!")

        # Caso os critério sejam atendidos, faz atribuição segura
        self._nome = novo_nome_limpo
        

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

        # Validação matemática do 2º dígito verificador
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

        # Valida o tipo de dado para garantir que o argumento passado seja uma string
        if not isinstance(novo_cpf, str):
            raise TypeError("O CPF deve ser enviado em formato de texto!")

        # Valida se o CPF não está vazio e não é composto somente por espaços
        if not novo_cpf.strip():
            raise ValueError("O campo CPF não pode estar vazio!")

        # Higienniza o CPF, deixando apenas os dígitos
        cpf_limpo = re.sub(r'[^0-9]', '', novo_cpf)

        # Valida o tamanho da string limpa
        if len(cpf_limpo) != 11:
            raise ValueError(f"O CPF deve conter exatamente 11 números. Você enviou {len(cpf_limpo)}.")

        # Realiza verificação matemática e, caso todas as verificaçoes sejam atendidas, atribui
        if self.__validar_cpf(cpf_limpo):
            self._cpf = cpf_limpo
        else:
            raise ValueError("O CPF informado possui dígitos verificadores incorretos.")


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def telefone(self):
        return self._telefone


    # Transforma a atribuição num Setter com validação obrigatória
    @telefone.setter
    def telefone(self, novo_telefone):

        # Valida o tipo de dado para garantir que o argumento passado seja uma string
        if not isinstance(novo_telefone, str):
            raise TypeError("O telefone deve ser enviado em formato de texto!")

        # Retira quaisquer coisas que não sejam dígitos (0-9)
        novo_telefone_limpo = re.sub(r'[^0-9]', '', novo_telefone)

        # Realiza verificação de tamanho mínimo e, caso todas as verificaçoes sejam atendidas, atribui
        if len(novo_telefone_limpo) == 11:
            self._telefone = novo_telefone_limpo

        # Notifica erro detalhado
        else:
            raise ValueError(f"O telefone deve conter exatamente 11 números (com DDD)! Você enviou {len(novo_telefone_limpo)}.")


    # Transforma a leitura num Getter disfarçado de atributo
    @property
    def email(self):
        return self._email


    # Transforma a atribuição num Setter com validação obrigatória
    @email.setter
    def email(self, novo_email):

        # Valida o tipo de dado para garantir que o argumento passado seja uma string
        if not isinstance(novo_email, str):
            raise TypeError("O e-mail deve ser enviado em formato de texto!")

        # Remove espaços em branco nas extremidades
        novo_email = novo_email.strip()

        # Realiza verificação estrutural de elementos essenciais e, caso todas as verificaçoes sejam atendidas, atribui
        if "@" in novo_email and "." in novo_email and " " not in novo_email:
            self._email = novo_email
            
        # Notifica erro detalhado
        else:
            raise ValueError("O formato do e-mail é inválido. Certifique-se de usar '@', '.' e não incluir espaços!")