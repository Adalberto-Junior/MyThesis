# Reimportar bibliotecas após reset do ambiente
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Dados corrigidos com base na revisão
artigos = [
    "Closing the Digital Divide", "Online Platform DE", "e-SpeechT Protocol",
    "Speech Intelligibility Aphasia", "Smart Assistants Proposal",
    "Home Voice Assistant", "Computer-Aided SLT", "Evaluation Speech System",
    "AI + Smart Assistants", "e-SpeechT Protocol 2", "NeuroSpeech", "Customization e-SpeechT"
]

# Critérios analisados
criterios = [
    "Semiautomático", "Terapeuta", "Idosos", "Idioma PT", 
    "Persona", "Cenário", "Requisitos"
]

# Matriz de presença (1) ou ausência (0) dos critérios
dados = [
    [1, 1, 1, 0, 0, 0, 0],  # Closing the Digital Divide
    [1, 1, 0, 0, 0, 0, 0],  # Online Platform DE
    [1, 1, 0, 0, 0, 0, 0],  # e-SpeechT Protocol
    [1, 1, 0, 0, 0, 0, 0],  # Speech Intelligibility Aphasia
    [1, 1, 0, 0, 0, 1, 0],  # Smart Assistants Proposal
    [1, 0, 1, 0, 0, 0, 0],  # Home Voice Assistant
    [1, 1, 0, 0, 0, 0, 0],  # Computer-Aided SLT
    [1, 1, 0, 0, 1, 1, 1],  # Evaluation Speech System
    [1, 1, 0, 0, 1, 1, 1],  # AI + Smart Assistants
    [1, 1, 0, 0, 1, 1, 0],  # e-SpeechT Protocol 2
    [1, 1, 0, 0, 0, 0, 0],  # NeuroSpeech
    [1, 1, 0, 0, 1, 1, 1]   # Customization e-SpeechT
]

df = pd.DataFrame(dados, columns=criterios, index=artigos)

# Plot do heatmap
plt.figure(figsize=(12, 6))
sns.heatmap(df, cmap="Greens", cbar=False, linewidths=.5, linecolor='gray', annot=True, fmt='d')
plt.title("Comparação entre Artigos Relacionados e Critérios Analisados", fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
# O código acima cria um heatmap que compara diferentes artigos relacionados a assistentes de voz e critérios analisados.
# Cada célula do heatmap indica a presença (1) ou ausência (0) de um critério específico em cada artigo.
# O heatmap é gerado usando a biblioteca Seaborn, que é uma extensão do Matplotlib para visualização de dados estatísticos.
# A matriz de dados foi corrigida para refletir a presença e ausência dos critérios de forma precisa.
# As bibliotecas Pandas e Matplotlib são usadas para manipulação de dados e visualização, respectivamente.
# As bibliotecas Seaborn e Matplotlib devem estar instaladas no ambiente Python para executar este código.
# Certifique-se de que as bibliotecas necessárias estão instaladas:
# pip install matplotlib seaborn pandas
# O código deve ser executado em um ambiente Python com suporte a gráficos, como Jupyter Notebook ou um script Python com interface gráfica.
# O heatmap resultante fornece uma visão clara de como cada artigo se alinha com os critérios analisados, facilitando a comparação visual.
# O heatmap é uma ferramenta útil para identificar rapidamente quais artigos atendem a quais critérios, permitindo uma análise mais aprofundada das abordagens e soluções propostas.            
