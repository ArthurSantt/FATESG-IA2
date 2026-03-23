import pandas as pd

dados = {
    'Nome': ['João', 'Maria'],
    'CPF': ['111.111.111-11', '222.222.222-22'],
    'Telefone': ['9999-9999', '8888-8888']
}
df = pd.DataFrame(dados)

del df['CPF']
removida = df.pop('Telefone')

print(removida)
print(df)