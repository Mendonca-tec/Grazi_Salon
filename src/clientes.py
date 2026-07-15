import os 
import time 
from src.dados import carregar_usuarios, salvar_usuarios
from src.servicos import carregar_catalogo, listar_servicos
from src.agendamentos import horarios_disponiveis, carregar_agendamentos, adicionar_agendamento 
from datetime import datetime
escolha = None


def limpar_tela():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')    

def servicos():

    limpar_tela()
    catalogo = carregar_catalogo()
    listar_servicos(catalogo)

    input("\nPressione Enter para sair")
  
def horarios():
    limpar_tela()
    catalogo = carregar_catalogo()
    if not listar_servicos(catalogo):
        input("\nPressione Enter para voltar...")
        return

    while True:
        id_servico = input("Informe o Número do serviço: ").strip()

        if id_servico in catalogo:
            break

        print("Serviço inválido. Tente novamente.")
    duracao = catalogo[id_servico]["duracao"]

    while True:
        data = input("Digite a data (dd/mm/aaaa): ").strip()

        try:
            datetime.strptime(data, "%d/%m/%Y")
            break
        except ValueError:
            print("Data em formato inválido. Tente novamente.")

    agendamentos = carregar_agendamentos()
    livres = horarios_disponiveis(agendamentos,data,duracao)
    if livres:
        print("\nHorários disponíveis:")
        for horario in livres:
            print(horario)
    else:
        print("Não há horários disponíveis nessa data.")
    input("\nPressione Enter para sair")
    

def agendamento(id_usuario, usuario):
    limpar_tela()
    agendamentos = carregar_agendamentos()
    catalogo_servicos = carregar_catalogo() 
    adicionar_agendamento(agendamentos, catalogo_servicos, id_usuario, usuario["nome"])
    input("\nPressione Enter para sair")  


def alterar_senha(id_usuario):
    usuarios = carregar_usuarios()

    senha = input("Digite sua nova senha: ")
    confirmar_senha = input ("Confirme sua senha: ")
    
    while senha != confirmar_senha:
        print("Senhas diferentes")
        senha = input("Digite sua nova senha: ")
        confirmar_senha = input("Confirme sua senha novamente:")
    
    usuarios[id_usuario]["senha"] = senha
    salvar_usuarios(usuarios)

    print("Senha alterada com sucesso!")        







def menu_cliente(id_usuario, usuario):
    global escolha
    escolha = None
    
    while escolha != 0:
        limpar_tela()
        print("GRAZY SALON")
        print(f"1 - Ver serviços\n2 - Horários livres\n3 - Fazer agendamento\n 4 - Alterar senha\n0 - Sair")
        
        while True:
            try:
                escolha = int(input("Deseja realizar qual ação? "))
                break
            except ValueError:
                print("Digite um número válido.")
            
        if escolha == 1:
            limpar_tela()
            servicos()
            
        elif escolha == 2:
            limpar_tela()
            horarios()
        elif escolha == 3:
            limpar_tela()
            agendamento(id_usuario, usuario)

        elif escolha == 4:
            limpar_tela()
            alterar_senha(id_usuario)
        elif escolha == 0:
            limpar_tela()
            print("Saindo...") 
            time.sleep(2.0)
            return      

        

