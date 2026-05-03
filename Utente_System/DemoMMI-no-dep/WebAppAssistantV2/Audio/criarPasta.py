import os

def criar_pasta_utilizador(base_path, nome_utilizador):
    caminho = os.path.join(base_path, nome_utilizador)
    os.makedirs(caminho, exist_ok=True)  # Cria a pasta se não existir
    
    return os.path.abspath(caminho) 

# Exemplo de uso
pasta = criar_pasta_utilizador(r"C:\Users\Adalb\Desktop\Dissertacao\DemoMMI-no-dep\DemoMMI-no-dep\WebAppAssistantV2\Audio", "joana_silva")
print(pasta)
# path = os.path.join( pasta, "audio.wav")
# print(path)
pasta = os.path.dirname(pasta)
if not os.access(pasta, os.W_OK):
    print(f"Atenção: Sem permissão de escrita na pasta: {pasta}")
else:
    print("Permissão de escrita confirmada.")

try:
    with open(os.path.join(os.path.dirname(pasta), "teste.txt"), "w") as f:
        f.write("teste")
    print("Escrita permitida.")
except PermissionError:
    print("Sem permissão de escrita.")

caminho_arquivo = r"C:\Users\Adalb\Desktop\Dissertacao\DemoMMI-no-dep\DemoMMI-no-dep\WebAppAssistantV2\Audio\Adalberto_Junior\REPA_TERO_Contar_numero_20250620_152153"
print(f"Comprimento do caminho: {len(caminho_arquivo)}")