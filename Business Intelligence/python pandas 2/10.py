import pandas as pd

dados = {'Nome': ['Ana', 'Bia', 'Caio'], 'Salário': [3000, 4000, 5000]}
df = pd.DataFrame(dados)

print(df.T)
print(df.dtypes)
print(df.size)
print(df.tail(2))