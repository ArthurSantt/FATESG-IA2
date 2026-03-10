import pandas as pd

dados = {'jan':100,"fev":200}
i = pd.Series(dados, index=['jan','fev','mar'])
print(i)