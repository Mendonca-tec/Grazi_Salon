import os
from src import dados
from src import servicos
from src import agendamentos
from src import cadastro

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def pausar():
    input("\nPressione ENTER para continuar...")

def menu_administrador(id_admin, admin):
    """Painel do administrador."""
    while True:
        limpar()
        print("="*40)
        print("        ====PYSALON====")
        print("      PAINEL ADMINISTRATIVO")
        print("="*40)
        print(f"Administrador: {admin['nome']}")
        print("\n1 - Ver Agendamentos")
        print("2 - Gerenciar Clientes")
        print("3 - Gerenciar Serviços")
        print("4 - Alterar minha senha")
        print("0 - Sair")
        op = input("\nEscolha: ")

        if op == "1":
            menu_agendamentos()
        elif op == "2":
            menu_clientes()
        elif op == "3":
            menu_servicos()
        elif op == "4":
            alterar_senha_admin(id_admin)
            pausar()
        elif op == "0":
            break
        else:
            print("Opção inválida.")
            pausar()

def alterar_senha_admin(id_admin):
    """Permite ao administrador trocar a própria senha (útil especialmente
    para trocar a senha padrão criada pelo auto-seed em dados.py)."""
    usuarios = dados.carregar_usuarios()

    while True:
        senha = input("Digite sua nova senha: ").strip()
        confirmar_senha = input("Confirme sua senha: ").strip()

        if not senha or not confirmar_senha:
            print("A senha não pode ficar em branco.")
            continue
        if senha != confirmar_senha:
            print("Senhas diferentes.")
            continue
        break

    usuarios[id_admin]["senha"] = senha
    dados.salvar_usuarios(usuarios)
    print("Senha alterada com sucesso!")

def menu_agendamentos():
    """Visualização dos agendamentos: por dia específico ou geral."""
    while True:
        limpar()
        print("=== AGENDAMENTOS ===")
        print("1 - Ver agendamentos de um dia")
        print("2 - Ver todos os agendamentos")
        print("0 - Voltar")
        op = input("Escolha: ")
        ag = dados.carregar_agendamentos()

        if op == "1":
            limpar()
            agendamentos.listar_agendamentos_do_dia(ag)
            pausar()
        elif op == "2":
            limpar()
            agendamentos.listar_agendamentos(ag)
            pausar()
        elif op == "0":
            break
        else:
            print("Opção inválida.")
            pausar()

def menu_clientes():
    """Gerenciamento de clientes."""
    while True:
        limpar()
        print("=== CLIENTES ===")
        print("1 - Ver clientes")
        print("2 - Cadastrar cliente")
        print("3 - Excluir cliente")
        print("0 - Voltar")
        op = input("Escolha: ")
        usuarios = dados.carregar_usuarios()

        if op=="1":
            algum_cliente = False
            for uid,u in usuarios.items():
                if u.get("tipo")=="cliente" and u.get("status","ativo")=="ativo":
                    algum_cliente = True
                    print("-"*40)
                    print(f"ID: {uid}")
                    print(f"Nome: {u.get('nome','')}")
                    print(f"E-mail: {u.get('email','')}")
                    print(f"Telefone: {u.get('telefone','')}")
            if not algum_cliente:
                print("Nenhum cliente ativo cadastrado.")
            pausar()
        elif op=="2":
            cadastro.criar_conta(usuarios)
            pausar()
        elif op=="3":
            cid=input("ID do cliente: ")
            if cid in usuarios and usuarios[cid].get("tipo")=="cliente" and usuarios[cid].get("status","ativo")=="ativo":
                confirmacao = input(f"Confirma excluir '{usuarios[cid]['nome']}'? (s/n): ").strip().lower()
                if confirmacao == "s":
                    # Soft-delete: marca como inativo em vez de apagar o
                    # registro, preservando o histórico de agendamentos
                    # (mesmo padrão de status usado em agendamentos.py)
                    usuarios[cid]["status"] = "inativo"
                    dados.salvar_usuarios(usuarios)
                    print("Cliente excluído.")
                else:
                    print("Exclusão cancelada.")
            else:
                print("Cliente não encontrado.")
            pausar()
        elif op=="0":
            break
        else:
            print("Opção inválida.")
            pausar()

def menu_servicos():
    """Gerenciamento de serviços."""
    while True:
        limpar()
        print("=== SERVIÇOS ===")
        print("1 - Adicionar serviço")
        print("2 - Editar serviço")
        print("3 - Excluir serviço")
        print("0 - Voltar")
        op=input("Escolha: ")
        serv=dados.carregar_servicos()
        if op=="1":
            servicos.adicionar_servico(serv)
            pausar()
        elif op=="2":
            servicos.editar_servico(serv)
            pausar()
        elif op=="3":
            servicos.remover_servico(serv)
            pausar()
        elif op=="0":
            break
        else:
            print("Opção inválida.")
            pausar()

if __name__=="__main__":
    menu_administrador("1",{"nome":"Administrador"})
