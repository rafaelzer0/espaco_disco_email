import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
import schedule
import time
import os

# Função para obter o espaço em disco C:
def get_disk_space():
    disk_usage = psutil.disk_usage('C:/')
    # 1KB = 1024 bytes, então precisamos converser para GB
    total =disk_usage.total / (1024 * 1024 * 1024)
    used = disk_usage.used / (1024 * 1024 * 1024)
    free = disk_usage.free / (1024 * 1024 * 1024)

    #return total, used, free
    return total, used, free

# Gerar gráfico
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


# Enviar email
def send_email(subject, body, attachment_path):
    # Config do server SMTP
    sender_email = 'seu_email@gmail.com'
    receiver_email = 'destinatario0@gmail.com'
    with open('sua_senha.txt') as f:
        senha =f.readlines()

    password = senha[0].strip()

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Anexar o gráfico
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

# Função para enviar relatório do C:
def daily_report():
    total, used, free = get_disk_space()
    subject = 'Relatório semanal do espaço em disco C:'
    body = f'Espaço total: {total:.2f} GB\nEspaço usado: {used:.2f} GB\nEspaço livre: {free:.2f} GB\nEm anexo, o gráfico mostrando o espaço total, usado e livre no disco C:'
    graph_path = generate_disk_graph() # Gera o gráfico
    send_email(subject, body, graph_path) # Envia o email com o gráfico como anexo

# Agendar para rodar semanalmente às segundas-feiras às 08hrs
schedule.every().monday.at('08:00').do(daily_report)

# Loop pra manter o script rodando
while True:
    schedule.run_pending()
    time.sleep(60) # Checar a cada minuto
