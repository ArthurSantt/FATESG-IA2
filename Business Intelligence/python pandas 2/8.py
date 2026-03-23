import pandas as pd

df_historico = pd.DataFrame({'Dados': range(1, 21)})
df_novo = df_historico[4:12]

print(df_novo)