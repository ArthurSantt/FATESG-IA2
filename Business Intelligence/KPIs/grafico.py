import matplotlib.pyplot as plt
import pandas as pd

dados = {
    'Ano': [2016, 2017, 2018, 2019],
    'Aparecida de Goiânia': [45.3, 46.9, 45.6, 48.7],
    'Goiânia': [59.2, 60.5, 64.8, 63.0]
}

df = pd.DataFrame(dados)

plt.figure(figsize=(10, 6))

plt.plot(df['Ano'], df['Goiânia'], marker='o', label='Goiânia', linewidth=3, color='#1f77b4')
plt.plot(df['Ano'], df['Aparecida de Goiânia'], marker='o', label='Aparecida de Goiânia', linewidth=3, color='#ff7f0e')

plt.title('Comparativo de Adequação da Formação Docente (%)', fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Porcentagem de Adequação (%)', fontsize=12)
plt.xticks(df['Ano'])
plt.ylim(0, 100)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

for i, txt in enumerate(df['Goiânia']):
    plt.annotate(f"{txt}%", (df['Ano'][i], df['Goiânia'][i]), textcoords="offset points", xytext=(0,10), ha='center')

for i, txt in enumerate(df['Aparecida de Goiânia']):
    plt.annotate(f"{txt}%", (df['Ano'][i], df['Aparecida de Goiânia'][i]), textcoords="offset points", xytext=(0,10), ha='center')

plt.tight_layout()
plt.show()