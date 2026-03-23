import pandas as pd

dados = {'Capital': ['Brasília', 'Buenos Aires', 'Santiago']}
df = pd.DataFrame(dados, index=['Brasil', 'Argentina', 'Chile'])

print(df.loc['Brasil'])