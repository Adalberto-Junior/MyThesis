from pymongo import MongoClient
import bcrypt
import time


# Function to hash a password
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# Function to store a user with a hashed password
def store_user(username, password):
    hashed_password = hash_password(password)
    user = {
        "username": username,
        "password": hashed_password
    }
    #collection.insert_one(user)
    print(f"User {username} stored successfully.")

# Conecte ao servidor MongoDB local
client = MongoClient("mongodb://localhost:27017/")
"""""
# Acesse um banco de dados (será criado automaticamente, se ainda não existir)
db = client["test"]

# Crie ou acesse uma coleção
colecao = db["user"]

# Insira um documento na coleção
documento = {"nome": "Adalberto", "cidade": "Aveiro", "linguagem": "Python"}
colecao.insert_one(documento)

print("Documento inserido com sucesso!")

# Procurar um documento específico
resultado = colecao.find_one({"nome": "Adalberto"})
print(resultado)
"""""

db = client["Casa_Viva"] #criar base de dados

userCollection = db["user"] #criar coleção de utilizadores
sessonCollection = db["sesson"] #criar coleção de sessões
schedulingCollection = db["Scheduling"] #criar coleção de agendamento
exerciseCollection = db["exercise"] #criar coleção de exercicios
resultsCollection = db["results"] #criar coleção de resultados
recordingCollection = db["recording"] #criar coleção de gravações
print("Coleções criadas com sucesso!")

# Inserir um documento na coleção:
#user:
#hashed_password = hash_password("12345678")
user = {
    "name": "Maria",
    "age": 70,
    "email": "maria@gmail.com",
    "password": hash_password("12345678"),
    "therapist": "Alice Fereira",
    "email_therapist": "talice@gmail.com"
    }
#userCollection.insert_one(user)

#sesson:
person = userCollection.find_one({"age": 70})
persons = userCollection.find()
for p in persons:
    print("person:", p)
sesson = {
    "date": "2021-06-12",
    "start": "14:00",
    "end":   "15:00",
    "user": person['_id'],
    }
sessonCollection.insert_one(sesson)

#scheduling:		
scheduling = {
    "title": "Sessão de Terapia",
    "date": "2021-06-12",
    "time": "14:00",
    "local": "Casa Viva",
    "description": "Sessão de Terapia com a Terapeuta Alice Ferreira",
    "guest": person['therapist'],
    "type": "Terapia Remota",
    "user": person['_id'],
    }
schedulingCollection.insert_one(scheduling)

#exercise:	
exercise = {
    "name": "Exercicio de repeticão de palavras",
    "description": "Exercicio de repeticão de palavras para melhorar a dicção",
    "steps": [
            {
                "step": 1,
                "description": "Repita a seguinte palavra 5 vezes, quando terminar diga terminei:",
                "word": "Fala"
            },
            {
                "step": 2,
                "description": "Repita a seguinte palavra 5 vezes, quando terminar diga terminei:",
                "word": "Tala"
            },
            {
                "step": 3,
                "description": "Repita a seguinte palavra 5 vezes, quando terminar diga terminei:",
                "word": "Cala"
            },
            {
                "step": 4,
                "description": "Repita a seguinte palavra 5 vezes, quando terminar diga terminei:",
                "word": "Bala"
            },
            {
                "step": 5,
                "description": "Repita a seguinte palavra 5 vezes, quando terminar diga terminei:",
                "word": "Mala"
            }],
    }
exerciseCollection.insert_one(exercise)
exercise = exerciseCollection.find_one({ "name": "Exercicio de repeticão de palavras" })
#recording:
recording = {
    "name": "exercicio_1.wav",
    "path": r"C:\Users\Adalb\Desktop\Dissertacao\DemoMMI-no-dep\DemoMMI-no-dep\WebAppAssistantV2\Audio\exercicio_1.wav",
    "date": "2021-06-12",
    "time": "14:00",
    "exercise": exercise['_id'],
    "user": person['_id'],
    }
recordingCollection.insert_one(recording)

#results:
recording = recordingCollection.find_one({ "name": "exercicio_1.wav" })					
results = {
    "date": "2021-06-12",
    "results": [
            {
                "f0": 0.1567,
                "unidade": "hz",
            },
            {
                "f01": 0.2367,
                "unidade": "hz",
            },
            {
                "pitch": 2.2367,
                "unidade": "hz",
            },
            {
                "pause": 0.2367,
                "unidade": "seg",
            },
            {
                "roquidão": 0.2367,
                "unidade": "hz",
            }],
    "recording": recording['_id'],
    }
resultsCollection.insert_one(results)
print("Documentos inseridos com sucesso!")
print("Recordings: ", recordingCollection.find())
print("Fim do programa!")