
from src import dados
from src import servicos
import math
from datetime import datetime, timedelta

# Horário de funcionamento do salão e tamanho de cada slot(Usado como tempo base para cada agendamento) fixo de atendimento
ABERTURA_MANHA = "08:00"
FECHAMENTO_MANHA = "12:00"
ABERTURA_TARDE = "14:00"
FECHAMENTO_TARDE = "18:00"
DURACAO_SLOT_MINUTOS = 30


def carregar_agendamentos():
    '''Carrega os agendamentos a partir do arquivo JSON'''
    return dados.carregar_agendamentos()


def _gerar_slots_periodo(inicio, fim):
    '''Gera os horários fixos (HH:MM) de um período, em passos de
    DURACAO_SLOT_MINUTOS, sem incluir o horário de fechamento.'''
    slots = []
    atual = datetime.strptime(inicio, "%H:%M")
    fim_dt = datetime.strptime(fim, "%H:%M")
    while atual < fim_dt:
        slots.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=DURACAO_SLOT_MINUTOS)
    return slots


def gerar_slots_do_dia():
    '''Gera todos os horários fixos de atendimento do dia (manhã + tarde),
    respeitando o intervalo de almoço entre 12:00 e 14:00.'''
    return _gerar_slots_periodo(ABERTURA_MANHA, FECHAMENTO_MANHA) + \
        _gerar_slots_periodo(ABERTURA_TARDE, FECHAMENTO_TARDE)


def _slots_necessarios(duracao_minutos):
    '''Quantos slots de DURACAO_SLOT_MINUTOS um serviço ocupa,
    arredondando pra cima (ex.: 40 min -> 2 slots de 30 min).'''
    return math.ceil(duracao_minutos / DURACAO_SLOT_MINUTOS)


def horarios_disponiveis(agendamentos, data, duracao_minutos):
    '''Retorna a lista de horários (HH:MM) onde é possível encaixar um
    serviço com a duração informada, no dia especificado — considerando
    os slots fixos de atendimento, o intervalo de almoço, e os agendamentos
    já ativos naquele dia (cada um ocupando os slots correspondentes à
    duração do seu próprio serviço).'''
    todos_slots = gerar_slots_do_dia()
    slots_precisos = _slots_necessarios(duracao_minutos)

    # Marca todos os slots já ocupados por agendamentos ativos nesse dia
    slots_ocupados = set()
    for ag in agendamentos.values():
        if ag["data"] != data or ag["status"] != "agendado":
            continue

        n_slots_ag = _slots_necessarios(ag.get("duracao_minutos", DURACAO_SLOT_MINUTOS))
        try:
            idx_inicio = todos_slots.index(ag["hora"])
        except ValueError:
            continue  # horário fora da grade fixa (dado antigo/legado) - ignora

        for i in range(idx_inicio, idx_inicio + n_slots_ag):
            if i < len(todos_slots):
                slots_ocupados.add(todos_slots[i])

    disponiveis = []
    for i in range(len(todos_slots)):
        candidatos = todos_slots[i:i + slots_precisos]

        # Não cabe o serviço inteiro até o fim da grade
        if len(candidatos) < slots_precisos:
            continue

        # Algum dos slots necessários já está ocupado
        if any(slot in slots_ocupados for slot in candidatos):
            continue

        # Garante que os slots são realmente consecutivos no tempo (evita
        # "atravessar" o intervalo de almoço, ex.: 11:30 + 60 min não pode
        # pular direto para 14:00)
        esperado = datetime.strptime(candidatos[0], "%H:%M")
        consecutivos = True
        for slot in candidatos:
            if slot != esperado.strftime("%H:%M"):
                consecutivos = False
                break
            esperado += timedelta(minutes=DURACAO_SLOT_MINUTOS)

        if consecutivos:
            disponiveis.append(candidatos[0])

    return disponiveis


def _horario_fim(hora_inicio, duracao_minutos):
    '''Calcula o horário de término (HH:MM) a partir do horário de início
    e da duração em minutos. Usado para exibir o intervalo completo que
    um agendamento ocupa (ex.: "08:00–09:00"), não só o horário de início.'''
    inicio_dt = datetime.strptime(hora_inicio, "%H:%M")
    fim_dt = inicio_dt + timedelta(minutes=duracao_minutos)
    return fim_dt.strftime("%H:%M")


def _proximo_id(agendamentos):
    '''Gera o próximo id sequencial, com base no maior id numérico
    já existente nos agendamentos. Ex.: se existem "1" e "2", o próximo
    será "3".'''
    if not agendamentos:
        return "1"
    return str(max(int(id_agendamento) for id_agendamento in agendamentos.keys()) + 1)


def listar_agendamentos(agendamentos):
    '''Mostra todos os agendamentos feitos até o momento. Retorna True se havia
    algo pra mostrar, False se a agenda estiver vazia.'''
    if not agendamentos:
        print("| Nenhum agendamento no momento.")
        return False

    print("\n| Agendamentos:")
    # Ordena pelo id numérico para a lista sempre aparecer em ordem (1, 2, 3...)
    for id_agendamento in sorted(agendamentos.keys(), key=int):
        agendamento = agendamentos[id_agendamento]
        duracao = agendamento.get("duracao_minutos", DURACAO_SLOT_MINUTOS)
        intervalo = f"{agendamento['hora']}–{_horario_fim(agendamento['hora'], duracao)}"
        print(
            f"| {id_agendamento} - {agendamento['nome_cliente']} | "
            f"{agendamento['nome_servico']} | {agendamento['data']} "
            f"{intervalo} | status: {agendamento['status']}"
        )
    return True


def listar_agendamentos_do_dia(agendamentos, data=None):
    '''Mostra os agendamentos de uma data específica, ordenados por horário.
    Pensada para o menu do admin ("ver agendamentos do dia"). Se `data` não
    for passada, pede ao usuário. Retorna True se havia algo pra mostrar
    naquele dia, False se a data for inválida ou não houver nada agendado.'''

    if data is None:
        data = input("| Ver agendamentos de qual data (ex: 25/03/2026): ").strip()

    try:
        datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        print("| Data em formato inválido.")
        return False

    # Filtra só os agendamentos daquele dia
    agendamentos_do_dia = {
        id_ag: ag for id_ag, ag in agendamentos.items() if ag["data"] == data
    }

    if not agendamentos_do_dia:
        print(f"| Nenhum agendamento para o dia {data}.")
        return False

    # Ordena por horário (string "HH:MM" ordena certo como texto,
    # já que o formato é sempre de dois dígitos)
    print(f"\n| Agendamentos do dia {data}:")
    for id_ag in sorted(agendamentos_do_dia, key=lambda i: agendamentos_do_dia[i]["hora"]):
        ag = agendamentos_do_dia[id_ag]
        duracao = ag.get("duracao_minutos", DURACAO_SLOT_MINUTOS)
        intervalo = f"{ag['hora']}–{_horario_fim(ag['hora'], duracao)}"
        print(
            f"| {intervalo} - {ag['nome_cliente']} | "
            f"{ag['nome_servico']} | status: {ag['status']}"
        )
    return True


def adicionar_agendamento(agendamentos, catalogo_servicos, id_cliente, nome_cliente):
    '''Cadastra um novo horário na agenda, checando conflito de horário
    antes de salvar.'''
    while True:
        print("| Fazer Agendamento")

        # Mostra a lista de serviços oferecidos pelo salão para o cliente escolher
        if not servicos.listar_servicos(catalogo_servicos):
            return

        id_servico = input("| Número do serviço: ").strip()
        if id_servico not in catalogo_servicos:
            print("| Serviço não encontrado.")
            return

        duracao_servico = catalogo_servicos[id_servico]["duracao"]

        # Seleção da data de atendimento
        data = input("| Data (ex: 25/03/2026): ").strip()
        try:
            datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            print("| Data em formato inválido.")
            continue

        # Mostra apenas os horários fixos (8h-12h e 14h-18h) que realmente
        # cabem esse serviço, já descontando os slots ocupados naquele dia
        slots_livres = horarios_disponiveis(agendamentos, data, duracao_servico)
        if not slots_livres:
            print("| Não há horários disponíveis nesse dia para esse serviço.")
            continue

        print(f"\n| Horários disponíveis em {data}:")
        for i, slot in enumerate(slots_livres, start=1):
            print(f"| {i} - {slot}–{_horario_fim(slot, duracao_servico)}")

        escolha = input("| Escolha o número do horário: ").strip()
        if not escolha.isdigit() or not (1 <= int(escolha) <= len(slots_livres)):
            print("| Opção inválida.")
            continue

        horario = slots_livres[int(escolha) - 1]

        novo_id_agendamento = _proximo_id(agendamentos)
        agendamentos[novo_id_agendamento] = {
            "id": novo_id_agendamento,
            "id_cliente": id_cliente,
            "nome_cliente": nome_cliente,
            "id_servico": id_servico,
            "nome_servico": catalogo_servicos[id_servico]["nome"],
            "data": data,
            "hora": horario,
            "duracao_minutos": duracao_servico,
            "status": "agendado",
        }

        dados.salvar_agendamentos(agendamentos)
        print("| Agendamento realizado com sucesso.")
        break


def cancelar_agendamento(agendamentos, id_cliente):
    '''Cancela um agendamento do cliente logado. Em vez de apagar o registro,
    apenas muda o status para "cancelado", preservando o histórico (como
    o documento sugere com os três status possíveis).'''

    # Filtra só os agendamentos DESSE cliente que ainda estão ativos
    agendamentos_cliente = {}
    for id_ag, ag in agendamentos.items():
        if ag["id_cliente"] == id_cliente and ag["status"] == "agendado":
            agendamentos_cliente[id_ag] = ag

    if not agendamentos_cliente:
        print("| Você não possui agendamentos ativos para cancelar.")
        return

    print("\n| Seus agendamentos ativos:")
    for id_ag, ag in agendamentos_cliente.items():
        duracao = ag.get("duracao_minutos", DURACAO_SLOT_MINUTOS)
        intervalo = f"{ag['hora']}–{_horario_fim(ag['hora'], duracao)}"
        print(f"| {id_ag} - {ag['nome_servico']}: {ag['data']} {intervalo}")

    id_cancelado = input("| Qual agendamento deseja cancelar (informe o número): ").strip()

    # Verifica dentro de agendamentos_cliente, não de agendamentos inteiro -(negativo)
    # impede o cliente de cancelar um agendamento de outra pessoa
    if id_cancelado not in agendamentos_cliente:
        print("| Agendamento não encontrado entre os seus.")
        return

    confirmacao = input("| Confirma o cancelamento? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("| Operação cancelada.")
        return

    agendamentos[id_cancelado]["status"] = "cancelado"
    dados.salvar_agendamentos(agendamentos)
    print("| Agendamento cancelado com sucesso.")
