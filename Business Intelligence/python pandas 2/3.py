import pandas as pd

indices = ['p1', 'p2', 'p3']
nomes = pd.Series(['Monitor', 'Teclado', 'Mouse'], index=indices)
precos = pd.Series([1200.00, 150.00, 80.00], index=indices)

df = pd.DataFrame({'Produto': nomes, 'Preço': precos})
print(df)