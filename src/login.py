import os
import curses

from src import dados


def cabecalho(stdscr):
    '''Desenha o título fixo no topo da tela'''
    stdscr.addstr(0, 2, "=== Salão de Beleza - Sistema de Agendamentos ===")


def entrada_do_sistema(stdscr):
    '''Função que se utiliza do curses para fazer com que o usuário escolha
    apenas entre as opções do menu (Login / Criar Conta), impedindo erros
    de digitação ou ValueError'''
    curses.curs_set(0)

    # (rótulo exibido, valor interno retornado) -> evita bug de comparação
    # de case (ex.: "Login" vs "login") que existia na versão anterior
    opcoes = [("Login", "login"), ("Criar Conta", "cadastro")]
    pos = 0
    # pos = posição do cursor, determina qual opção está selecionada

    while True:
        stdscr.clear()
        cabecalho(stdscr)

        for i, (rotulo, _valor) in enumerate(opcoes):
            if i == pos:
                stdscr.addstr(i + 2, 2, rotulo, curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 2, rotulo)

        tecla = stdscr.getch()

        if tecla == curses.KEY_UP:
            pos = (pos - 1) % len(opcoes)
        elif tecla == curses.KEY_DOWN:
            pos = (pos + 1) % len(opcoes)
        elif tecla == 10:  # Enter
            return opcoes[pos][1]  # retorna "login" ou "cadastro"


def login(usuarios):
    '''Função referente ao login. Busca o usuário pelo e-mail e senha
    informados dentro do dicionário único de usuários (que contém tanto
    clientes quanto administradores, diferenciados pelo campo "tipo",
    conforme a estrutura de dados sugerida no documento) e direciona
    para o menu correspondente.'''

    # Import feito aqui dentro (e não no topo do arquivo) para evitar
    # import circular, já que clientes.py e admin.py também vão importar
    # coisas de login.py/dados.py
    from src.clientes import menu_cliente
    from src.admin import menu_administrador

    while True:
        email = input("| Email: ").strip().lower()
        senha = input("| Senha: ").strip()

        if not email or not senha:
            os.system("cls" if os.name == "nt" else "clear")
            print("| Email e senha não podem ficar em branco")
            continue

        usuario_encontrado = None
        id_encontrado = None

        for id_usuario, dados_usuario in usuarios.items():
            if dados_usuario["email"].lower() == email and dados_usuario["senha"] == senha:
                # Contas com status "inativo" (cliente excluído pelo admin)
                # não conseguem mais logar, mesmo com email/senha corretos
                if dados_usuario.get("status", "ativo") != "ativo":
                    continue
                usuario_encontrado = dados_usuario
                id_encontrado = id_usuario
                break

        if usuario_encontrado is None:
            os.system("cls" if os.name == "nt" else "clear")
            print("| Email ou senha inválido")
            continue

        os.system("cls" if os.name == "nt" else "clear")
        print(f"Seja Bem Vindo(a) {usuario_encontrado['nome']}")

        if usuario_encontrado["tipo"] == "admin":
            return menu_administrador(id_encontrado, usuario_encontrado)
        else:
            return menu_cliente(id_encontrado, usuario_encontrado)
