# Monitoramento Automático do Espaço em Disco com Python

Este projeto contém um script Python que monitora o espaço em disco do sistema e envia um relatório semanal automatizado por e-mail. Ele coleta informações sobre o uso do disco, gera um gráfico e envia um e-mail com o gráfico anexado.

## Funcionalidades

- **Coleta de dados de espaço em disco**: Usa a biblioteca `psutil` para coletar informações sobre o espaço total, usado e livre do disco C:.
- **Geração de gráfico**: Utiliza a `matplotlib` para criar um gráfico de barras visualizando o uso do disco.
- **Envio de e-mail**: Envia um e-mail com o gráfico gerado em anexo utilizando o servidor SMTP do Gmail.
- **Agendamento semanal**: O script é agendado para rodar semanalmente usando a biblioteca `schedule`.

## Pré-requisitos

- Python 3.x
- Bibliotecas Python:
  - `psutil` (para monitoramento do disco)
  - `matplotlib` (para geração do gráfico)
  - `smtplib` (para envio de e-mails)
  - `schedule` (para agendamento do script)

### Você pode instalar as dependências necessárias com o seguinte comando:
pip install psutil matplotlib schedule

## Configuração do Gmail:

Acesse sua conta do Gmail e permita o acesso a "Aplicativos menos seguros".
Crie um arquivo .txt contendo a senha do seu e-mail do Gmail.
