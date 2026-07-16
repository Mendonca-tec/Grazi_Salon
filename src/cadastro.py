import re
import uuid

from src import dados


def validar_email(email):
    ''' Função desenvolvida para tratamento de emails.
        Onde verifica se os email são validos'''
    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(padrao, email) is not None


def criar_conta(usuarios):
    ''' Cria uma nova conta e a adiciona ao dicionário de usuários, sempre
    com tipo "cliente" (como pede o documento). Pede os dados, valida, e
    salva no arquivo. Retorna o id do novo usuário em caso de sucesso, ou
    None se o usuário cancelar/houver algum problema irreparável — usada
    tanto pelo cadastro público (cadastro()) quanto pelo admin, que cadastra
    clientes sem precisar fazer login logo em seguida.'''

    print("| Preencha todos os dados a seguir.")
    while True:
        nome = input("| Nome: ")
        telefone = input("| Telefone/Celular: ")
        email = input("| E-mail: ").lower().strip()
        senha = input("| Senha: ")
        confirmar_senha = input("| Confirma senha: ")

        # Verifica se o usuário não deixou algum campo em branco
        if not all([nome, telefone, email, senha, confirmar_senha]):
            print("| Todos os campos devem ser preenchidos.")
            continue

        # Verifica se a senha é igual a sua confirmação
        if senha != confirmar_senha:
            print("| Senhas diferentes!!")
            continue

        # Verifica se o email é válido
        if not validar_email(email):
            print("| O e-mail informado é inválido.")
            continue

        # Verifica se o email já existe no banco de dados
        email_existente = False
        for id_usuario, dados_usuario in usuarios.items():
            if dados_usuario["email"].lower() == email:
                email_existente = True
                break

        if email_existente:
            print("| E-mail já em uso")
            continue

        # Uso da biblioteca uuid para gerar um id único
        novo_id = str(uuid.uuid4())

        usuarios[novo_id] = {
            "id": novo_id,
            "nome": nome.strip(),
            "email": email,
            "telefone": telefone.strip(),
            "senha": senha,
            "tipo": "cliente",
        }

        # Persiste a alteração no arquivo JSON
        dados.salvar_usuarios(usuarios)
        print("| Conta criada com sucesso!")
        return novo_id


def cadastro(usuarios):
    ''' Fluxo de cadastro PÚBLICO (tela inicial: Login / Criar Conta).
    Cria a conta e, em seguida, já direciona para o login — comportamento
    que só faz sentido nesse contexto, e não quando é o admin quem está
    cadastrando um cliente pelo painel administrativo (ver criar_conta).'''

    # Import feito aqui dentro para evitar import circular com login.py
    from src.login import login

    criar_conta(usuarios)
    return login(usuarios)
