import pandas as pd

dados = {'Sede A': [1000, 2000, 3000], 'Sede B': [1500, 2500, 3500]}
df = pd.DataFrame(dados)

df['Total Vendas'] = df['Sede A'] + df['Sede B']
df['Imposto'] = df['Sede A'] * 0.10

print(df)