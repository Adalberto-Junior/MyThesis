import win32com.client as win32
import time
import zipfile
import os

#Zipar ficheiro
def zipar_ficheiros(caminho_zip, ficheiros):
    with zipfile.ZipFile(caminho_zip, 'w') as zipf:
        for ficheiro in ficheiros:
            zipf.write(ficheiro, os.path.basename(ficheiro))


pasta = r'..\Grafico'
ficheiros = []
for raiz, diretorios, arquivos in os.walk(pasta):
    for arquivo in arquivos:
        ficheiros.append(os.path.join(raiz, arquivo))

# Exibir todos os ficheiros encontrados
print(ficheiros)

# Exemplo de uso
#icheiros_para_zipar = ['prosody_graph_1.png', 'prosody_graph_2.png']
caminho_zip = '.\imagem.zip'
zipar_ficheiros(caminho_zip, ficheiros)

#Criar integração com o outlook
outlook = win32.Dispatch('outlook.application')

#crear um item, email. do outlook
email = outlook.CreateItem(0)
tempo = 10
peso = 150

#configurar as informaçoes do email:
email.To = 'adalberton2ta@gmail.com'
email.Subject = 'Testando o email automatico'
email.HTMLBody = f'''
<p>Bom dia Adalberto, espero que esteja bem. Aqui é o Júnior</p>

<p>Estou enviando este email para testar o envio de email de forma automatico.Vai ser necessário para enviar o email ao Terapeuta.</p>
<p>Será util para a dissertação.</p>
<p>Estou no dia {tempo} e vendi {peso} gramas</p>
<p><b>Em Anexo envio os ficheiro</b></p>

<p>Cumprimentos,</p>
<p>Júnior</p>

'''
anexo = r'C:\Users\Adalb\Desktop\Dissertacao\DemoMMI-no-dep\DemoMMI-no-dep\WebAppAssistantV2\Audio\imagem.zip'
email.Attachments.Add(anexo)
email.Send()
print("Enviando .",end="")
time.sleep(1)
print(".",end="")
time.sleep(1)
print(".",end="")
time.sleep(1)
print(".")
time.sleep(2)
print("Email enviado!")
