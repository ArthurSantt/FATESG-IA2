import requests
import pymongo

# 1. Conectar ao MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["startup"]
collection = db["funcionarios"]

# 2. Obter dados da API
url = "https://randomuser.me/api/?results=10&nat=br"
response = requests.get(url).json()

# 3. Processar e organizar os dados
funcionarios = []
for user in response["results"]:
    idade = user["dob"]["age"]
    funcionarios.append({
        "nome": f"{user['name']['first']} {user['name']['last']}",
        "idade": idade,
        "email": user["email"],
        "telefone": user["phone"],
        "cargo": "Desenvolvedor" if idade < 30 else "Gerente",
        "salario": 7000 if idade < 30 else 12000,
        "setor": "TI"
    })

# 4. Inserir no Banco de Dados
collection.insert_many(funcionarios)
print("Dados inseridos com sucesso!")