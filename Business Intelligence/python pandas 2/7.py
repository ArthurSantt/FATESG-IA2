import pandas as pd

carros = {'Modelo': ['Carro 1', 'Carro 2', 'Carro 3', 'Carro 4', 'Carro 5', 'Carro 6']}
df = pd.DataFrame(carros)

print(df.iloc[3:5])