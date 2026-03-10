import pandas as pd

dados = {
    'Produto': ['Teclado', 'Mouse', 'Monitor'],
    'Preço': [150, 80, 950],
    'Estoque': [10, 25, 5]
}

df = pd.DataFrame(dados)

produtos = df['Produto']

caros = df[df['Preço'] > 100]

print("Apenas Produtos:")
print(produtos)
print("\nProdutos acima de 100 reais:")
print(caros)