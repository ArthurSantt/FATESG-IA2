import pandas as pd
from pymongo import MongoClient

def conectar_e_exibir():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        
        db = client['AtividadeNetflix']
        collection = db['filmes']
        
        dados_do_banco = list(collection.find())
        
        df = pd.DataFrame(dados_do_banco)
        
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
    
        print("\n--- Top 5 Amostras do Dataset Netflix ---")
        print(df.head(5))
        
    except Exception as e:
        print(f"Erro ao conectar ou processar dados: {e}")

if __name__ == "__main__":
    conectar_e_exibir()