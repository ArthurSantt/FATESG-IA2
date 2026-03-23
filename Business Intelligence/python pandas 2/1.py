import pandas as pd

dados = {
    'Nome': ['Ana', 'Bruno', 'Carlos', 'Diana', 'Eduardo'],
    'Idade': [20, 22, 21, 23, 20]
}
df = pd.DataFrame(dados)
print(df)