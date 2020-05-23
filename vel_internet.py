"""
    DESCRIÇÃO: Testa velocidade da internet atravez do speedtest
"""

# BIBLIOTECAS
import smtplib
import subprocess
import json
import os

from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path

from getpass import getpass

# VARIAVEIS
MY_EMAIL_ADDRESS = input('Digite o usuário: ')
MY_EMAIL_PASSWORD = getpass('Digite a senha: ')
SMTP_SERVER = 'smtp-mail.outlook.com'
PORT_SMTP_SERVER = 587
SUBJECT_EMAIL = 'STATUS VELOCIDADE INTERNET'
ARQUIVO_MODELO = 'template_mail.html'
ARQUIVO_CONTATOS = 'mycontacts.txt'
FILE_JSON = 'speedtest.json'

# FUNCOES
def read_file_template(filename):
    with open(filename, mode='r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def get_contacts(filename):
    names = []
    emails = []

    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
        return names, emails

def send_email():
    try:
        names, emails = get_contacts(ARQUIVO_CONTATOS)    # read contacts
        message_template = read_file_template(ARQUIVO_MODELO)

        with open(FILE_JSON, mode='r', encoding='utf-8') as f:
            data = json.load(f)

        # set up the SMTP server
        s = smtplib.SMTP(host=SMTP_SERVER, port=PORT_SMTP_SERVER)
        s.starttls()
        s.login(MY_EMAIL_ADDRESS, MY_EMAIL_PASSWORD)

        # For each contact, send the email:
        for name, email in zip(names, emails):
            msg = MIMEMultipart()   # create a message

            # add in the actual person name to the message template
            upload = format((int(data['upload']['bytes'])) / 1024**2, '.2f')
            download = format((int(data['download']['bytes'])) / 1024**2, '.2f')
            message = message_template.substitute(PERSON_NAME=name.title(), EMPRESA=str(data['isp']), IP_EXTERNO=str(data['interface']['externalIp']), JITTER=str(data['ping']['jitter']), LATENCIA=str(data['ping']['latency']), DOWNLOAD=download, UPLOAD=upload)

            # Prints out the message body for our sake
            #print(message)

            # setup the paramessagemeters of the message
            msg['From'] = MY_EMAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = SUBJECT_EMAIL

            # add in the message body
            msg.attach(MIMEText(message, 'html'))
            #msg.attach(MIMEText(html, 'html'))
            
            # send the message via the server set up earlier.
            s.send_message(msg)
            
            del msg

        # Terminate the SMTP session and close the connection
        s.quit()
    
        return True
    except:
        return False

def get_speedtest():
    try:
        output_json_file = subprocess.run(['speedtest', '--server-id=16155', '-f', 'json'], capture_output=True)
        with open(FILE_JSON, mode='w', encoding='utf-8') as output_json:
            output_json.write(str(output_json_file.stdout.decode('utf-8')))
        return True
    except:
        return False

def main():
    if get_speedtest():
        print('Enviando E-mail(s)')
        if send_email():
            print('E-mail(s) enviados')
        else:
            print('Erro ao enviado e-mail(s)')
    else:
        print('Erro para fazer o teste de velocidade')
        send_email()

# INICIALIZACAO
if __name__ == "__main__":
    print('Inicio do teste de velocidade')
    main()
    #send_email()