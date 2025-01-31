import psutil
import smtplib
import os
import json
import time
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt

print('Script iniciado...')

# Função para obter o espaço em disco C:
def get_disk_space():
    disk_usage = psutil.disk_usage('C:/')
    # 1KB = 1024 bytes, então precisamos converser para GB
    total =disk_usage.total / (1024 * 1024 * 1024)
    used = disk_usage.used / (1024 * 1024 * 1024)
    free = disk_usage.free / (1024 * 1024 * 1024)

    

    #return total, used, free
    return total, used, free

# Obter o tamanho de uma pasta
def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
            
    return total_size / (1024 * 1024)


# Monitorar o crescimento das pastas
def monitor_folder_growth(folder_paths, log_file='registro_crescimento_log.json'):
    growth_data = {}  # Inicializando growth_data antes de usá-la

    # Verifica se o arquivo de log existe e tenta carregá-lo
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                growth_data = json.load(f)
                print(f"Arquivo {log_file} carregado com sucesso!")  # Mensagem para verificar
        except json.JSONDecodeError:
            print(f"O arquivo {log_file} está vazio ou corrompido. Criando um novo arquivo.")
            growth_data = {}  # Se o arquivo for vazio ou corrompido, inicializa com um dicionário vazio
    else:
        print(f"Arquivo {log_file} não encontrado, criando novo arquivo.")

    current_sizes = {}
    for folder in folder_paths:
        current_size = get_folder_size(folder)
        if folder not in growth_data:
            growth_data[folder] = {'last_size': current_size, 'growth_rate': 0, 'last_checked': time.time(), 'weekly_growth': 0}

        last_size = growth_data[folder]['last_size']
        time_diff = time.time() - growth_data[folder]['last_checked']

        if time_diff == 0:  # Se o tempo desde a última verificação for zero, evitar divisão por zero
            grow_rate = 0  # Não podemos calcular o crescimento se o tempo for zero
        else:
            # Calcula a taxa de crescimento por hora
            grow_rate = (current_size - last_size) / (time_diff / 3600)

        # Calcula a taxa de crescimento
        growth_data[folder]['growth_rate'] = grow_rate
        growth_data[folder]['last_size'] = current_size
        growth_data[folder]['last_checked'] = time.time()

        # Armazena o crescimento semanal (simples diferença entre o tamanho atual e o tamanho registrado na última verificação)
        weekly_growth = current_size - growth_data[folder]['last_size']
        growth_data[folder]['weekly_growth'] = weekly_growth

        current_sizes[folder] = current_size

    # Salva os dados atualizados no arquivo de log
    with open(log_file, 'w') as f:
        json.dump(growth_data, f, indent=4)

    return growth_data
    

# Gerar gráfico Disco C:
def generate_disk_graph():
    total, used, free = get_disk_space()

    # Criar gráfico
    labels = ['Total', 'Usado', 'Livre']
    sizes = [total, used, free]

    fig, ax = plt.subplots()
    ax.bar(labels, sizes, color=['blue', 'orange', 'green'])

    ax.set_ylabel('Espaço em GB')
    ax.set_title('Uso do Disco C:')

    # Salvar o gráfico em um arquivo temporário
    graph_path = 'disk_usage_graph.png'
    plt.savefig(graph_path)
    plt.close()

    return graph_path


# Gerar gráfico de Crescimento semanal das pastas
def generate_growth_graph(growth_data):
    folders = list(growth_data.keys())
    weekly_growth = [data['weekly_growth'] for data in growth_data.values()]

    fig, ax = plt.subplots()
    ax.bar(folders, weekly_growth, color='purple')

    ax.set_ylabel('Crescimento Semanal (MB)')
    ax.set_title('Crescimento Semanal das Pastas')

    graph_path = 'weekly_growth_graph.png' # Trocar nome aquivo da imagem
    plt.savefig(graph_path)
    plt.close()

    return graph_path


# Enviar email
def send_email(subject, body, attachment_path):
    # Config do server SMTP
    sender_email = 'rafaelzerort@gmail.com'
    receiver_email = 'rafaelndsilva0@gmail.com'
    with open('senha_rafaelzero.txt') as f:
        senha =f.readlines()

    password = senha[0].strip()

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Anexar o gráfico
    for attachment_path in attachment_path:
        with open(attachment_path, 'rb') as f:
            img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(attachment_path))
            msg.attach(image)


    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print('Relatório semanal enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar o email: {e}')


# Gerar relatório semanal
def weekly_report():
    # Coleta dados de uso do disco 
    total, used, free = get_disk_space()

    # Coleta dados sobre o crescimento das pastas
    folders_to_monitor = ['C:/Users', 'D:/Projetos', 'C:/Program Files'] # Alterar as pastas para coletar os dados. 
    growth_data = monitor_folder_growth(folders_to_monitor)

    # Ordenar as pastas pelo maior crescimento (taxa de crescimento)
    top_folders = sorted(growth_data.items(), key=lambda x: x[1]['growth_rate'], reverse=True)[:5]

    # Corpo do email
    subject = 'Relatório semanal do espaço em disco C:'
    body = f'Espaço total: {total:.2f} GB\nEspaço usado: {used:.2f} GB\nEspaço livre: {free:.2f} GB\n\n'
    body += '5 Pastas com Maior taxa de crescimento (MB/h):\n'

    # Exibir as 5 pastas com maior crescimento
    for folder, data in top_folders:
        body += f'{folder}: Crescimento: {data["growth_rate"]:.2f} MB/h, Tamanho Atual: {data["last_size"]:.2f} MB, Crescimento Semanal: {data["weekly_growth"]:.2f} MB\n'

    # Comparar com a semana anterior(se houver dados da semana anterior.)
    prev_growth_data = {}
    if os.path.exists('registro_crescimento_log.json'):
        with open('registro_crescimento_log.json', 'r') as f:
            prev_growth_data = json.load(f)

    body += '\nComparação com a semana anterior:\n'
    for folder, data in top_folders:
        prev_weekly_growth = prev_growth_data.get(folder, {}).get('weekly_growth', 0)
        growth_diff = data['weekly_growth'] - prev_weekly_growth
        body += f'{folder}: Diferença de Crescimento: {growth_diff:.2f} MB\n'

        
    # Gerar gráficos 
    disk_graph_path = generate_disk_graph()
    growth_graph_path = generate_growth_graph(growth_data)

    # Enviar o email com os gráficos
    send_email(subject, body, [disk_graph_path, growth_graph_path])


# Agendar a execução semanal
schedule.every().friday.at('01:24').do(weekly_report)

# Loop pra manter o script rodando
while True:
    schedule.run_pending()
    time.sleep(60) 
