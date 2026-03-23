import pandas as pd

df_loja1 = pd.DataFrame({'Produto': ['A', 'B'], 'Estoque': [10, 20]})
df_loja2 = pd.DataFrame({'Produto': ['C', 'D'], 'Estoque': [30, 40]})

df_resultado = pd.concat([df_loja1, df_loja2])
print(df_resultado)