import redis
import base64
import os

db = redis.Redis(host='localhost', port=6379, decode_responses=True)

def gerenciar_fluxo():
    try:
        if db.ping():
            print("--> Conexão estabelecida com o servidor Redis.")
    except Exception:
        print("--> Falha: Servidor Redis não encontrado.")
        return

    origem = "meu_teste.png"
    tag = "armazenamento_v1"
    destino = "copia_final.png"

    path_script = os.path.dirname(os.path.abspath(__file__))
    path_img = os.path.join(path_script, origem)

    if os.path.exists(path_img):
        print(f"--> Localizado: {origem}")
        
        with open(path_img, "rb") as arq:
            conversao = base64.b64encode(arq.read()).decode('utf-8')
            db.set(tag, conversao)
        print(f"--> Sucesso: Imagem enviada para a chave [{tag}].")

        recuperado = db.get(tag)
        if recuperado:
            print("--> Extraindo dados do banco...")
            with open(destino, "wb") as f_saida:
                f_saida.write(base64.b64decode(recuperado))
            print(f"--> Finalizado: Arquivo '{destino}' criado com sucesso.")
    else:
        print(f"--> Erro: O arquivo '{origem}' não está na pasta {path_script}.")

if __name__ == "__main__":
    print("--- MONITOR DE TRANSAÇÕES NOSQL ---")
    gerenciar_fluxo()
    print("----------------------------------")