import re

def validar_cpf(cpf: str) -> bool:
    """
    Função responsável por realizar a "limpeza" e validação do CPF digitado,
    removendo qualquer coisa que não seja um dígito (0-9), impedindo CPFs como "00000000000",
    verificando o tamanho do CPF digitado e executando verificação matemática de dígitos verificadores.
    """

    # Retira quaisquer coisas que não sejam dígitos (0-9)
    cpf = re.sub(r'[^0-9]', '', cpf)

    # Barra CPFs como "00000000000", "11111111111", "22222222222", etc.
    if len(set(cpf)) == 1:
        return False

    # Verifica o tamanho exato do CPF digitado
    if len(cpf) != 11:
        return False

    # Validação matemática do 1º dígito verificador
    dig_veri_1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig_veri_1 = (dig_veri_1 * 10) % 11

    if dig_veri_1 == 10 or dig_veri_1 == 11:
        dig_veri_1 = 0

    if str(dig_veri_1) != cpf[9]:
        return False

    # Validação matemática do 2º dígito verificador
    dig_veri_2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig_veri_2 = (dig_veri_2 * 10) % 11

    if dig_veri_2 == 10 or dig_veri_2 == 11:
        dig_veri_2 = 0

    if str(dig_veri_2) != cpf[10]:
        return False

    # Valida o CPF caso tenha passado por todas as verificações
    return True

# Construção da classe
class Pessoa:
    """
    Classe base que concentra os dados de identificação comuns a qualquer
    pessoa na instituição (nome, CPF, telefone e e-mail).
    """

    def __init__(self, nome: str, cpf: str, telefone: str, email: str) -> None:

        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email


    @property
    def nome(self):
        return self._nome


    @nome.setter
    def nome(self, novo_nome):

        if not isinstance(novo_nome, str):
            raise TypeError("O nome deve ser enviado em formato de texto!")

        # Retira caracteres inválidos e transforma tudo em minúsculas para criar a base
        novo_nome = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', novo_nome).lower()

        if not novo_nome or len(novo_nome) < 6:
            raise ValueError("O nome da pessoa deve conter pelo menos 6 letras válidas!")

        # Lista de exceções
        excecoes = {'de', 'da', 'do', 'das', 'dos', 'a', 'e', 'o', 'as', 'os', 'em', 'por', 'para', 'com'}

        # Formatação inteligente usando List Comprehension
        # Capitaliza a primeira palavra (índice 0) OU se a palavra NÃO estiver nas exceções
        palavras = [
            p.capitalize() if i == 0 or p not in excecoes else p
            for i, p in enumerate(novo_nome.split())
        ]

        self._nome = " ".join(palavras)


    @property
    def cpf(self):
        return self._cpf


    @cpf.setter
    def cpf(self, novo_cpf):

        if not isinstance(novo_cpf, str):
            raise TypeError("O CPF deve ser enviado em formato de texto!")

        if not novo_cpf.strip():
            raise ValueError("O campo CPF não pode estar vazio!")

        # Higieniza o CPF, deixando apenas os dígitos
        novo_cpf = re.sub(r'[^0-9]', '', novo_cpf)

        if len(novo_cpf) != 11:
            raise ValueError(f"O CPF deve conter exatamente 11 números. Você enviou {len(novo_cpf)}!")

        # Realiza verificação matemática e, caso todas as verificações sejam atendidas, atribui
        if validar_cpf(novo_cpf):
            self._cpf = novo_cpf
        else:
            raise ValueError("O CPF informado possui dígitos verificadores incorretos!")


    @property
    def telefone(self):
        return self._telefone


    @telefone.setter
    def telefone(self, novo_telefone):

        if not isinstance(novo_telefone, str):
            raise TypeError("O telefone deve ser enviado em formato de texto!")

        # Retira quaisquer coisas que não sejam dígitos (0-9)
        novo_telefone = re.sub(r'[^0-9]', '', novo_telefone)

        # Realiza verificação de tamanho mínimo e, caso todas as verificações sejam atendidas, atribui
        if len(novo_telefone) == 11:
            self._telefone = novo_telefone
        else:
            raise ValueError(
                f"O telefone deve conter exatamente 11 números (com DDD)! Você enviou {len(novo_telefone)}.")


    @property
    def email(self):
        return self._email


    @email.setter
    def email(self, novo_email):

        if not isinstance(novo_email, str):
            raise TypeError("O e-mail deve ser enviado em formato de texto!")

        # Remove espaços em branco nas extremidades
        novo_email = novo_email.strip()

        # Realiza verificação estrutural de elementos essenciais
        # Caso todas as verificações sejam atendidas, atribui
        if "@" in novo_email and "." in novo_email and " " not in novo_email:
            self._email = novo_email
        else:
            raise ValueError("O formato do e-mail é inválido. Certifique-se de usar '@', '.' e não incluir espaços!")