import pandas as pd

funcionarios = [
    {'Nome': 'Ana', 'Cargo': 'Analista'},
    {'Nome': 'Bruno', 'Cargo': 'Gerente', 'Bonus': 500}
]
df = pd.DataFrame(funcionarios)

print(df)