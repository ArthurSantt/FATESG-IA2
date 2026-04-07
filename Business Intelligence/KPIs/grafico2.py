import matplotlib.pyplot as plt
import pandas as pd

anos_full = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
vol_aparecida = [3994, 4107, 4203, 4297, 4139, 3943, 3843, 4000, 3998, 4179]
vol_goiania = [13114, 13300, 13093, 13320, 13100, 12842, 12250, 12870, 13258, 13202]

plt.figure(figsize=(12, 6))

plt.bar([a - 0.2 for a in anos_full], vol_goiania, width=0.4, label='Goiânia', color='#1f77b4')
plt.bar([a + 0.2 for a in anos_full], vol_aparecida, width=0.4, label='Aparecida de Goiânia', color='#ff7f0e')

plt.title('Volume Total de Docentes (2015-2024)', fontsize=14, fontweight='bold')
plt.ylabel('Quantidade de Docentes')
plt.xticks(anos_full)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()