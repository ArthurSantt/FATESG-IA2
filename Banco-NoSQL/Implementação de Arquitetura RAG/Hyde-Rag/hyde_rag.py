import os
import time
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client import models
from openai import OpenAI

# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────

CSV_PATH = Path("wiki_movie_plots_deduped.csv")
COLLECTION_NAME = "wiki_movies_hyde"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MARITACA_MODEL_NAME = "sabiazinho-4"
MARITACA_BASE_URL = "https://chat.maritaca.ai/api"
TOP_K = 5
BATCH_SIZE = 64
MAX_ROWS = 2000  # usa só os primeiros 2000 filmes pra indexar rápido

# ─────────────────────────────────────────────
# CARREGAR CHAVE
# ─────────────────────────────────────────────

load_dotenv()
MARITACA_API_KEY = os.getenv("MARITACA_API_KEY")
if not MARITACA_API_KEY:
    raise ValueError("Chave MARITACA_API_KEY não encontrada no .env")

print("Chave da Maritaca carregada.")

# ─────────────────────────────────────────────
# CARREGAR CSV
# ─────────────────────────────────────────────

print("Carregando dataset...")
df = pd.read_csv(CSV_PATH, on_bad_lines="skip")
df.columns = [col.strip() for col in df.columns]
df = df.dropna(subset=["Title", "Plot"])
df = df.fillna("")
df = df.reset_index(drop=True)
df = df.head(MAX_ROWS)
print(f"Dataset carregado: {len(df)} filmes.")

# ─────────────────────────────────────────────
# MONTAR TEXTO DE CADA FILME
# ─────────────────────────────────────────────

def build_movie_text(row):
    return (
        f"Title: {row.get('Title', '')}. "
        f"Year: {row.get('Release Year', '')}. "
        f"Genre: {row.get('Genre', '')}. "
        f"Director: {row.get('Director', '')}. "
        f"Cast: {row.get('Cast', '')}. "
        f"Plot: {row.get('Plot', '')}"
    )

df["rag_text"] = df.apply(build_movie_text, axis=1)
print("Textos dos filmes montados.")
print("Exemplo:")
print(df.loc[0, "rag_text"][:300])

# ─────────────────────────────────────────────
# CARREGAR MODELO DE EMBEDDING
# ─────────────────────────────────────────────

print("\nCarregando modelo de embeddings...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
VECTOR_SIZE = embedding_model.get_sentence_embedding_dimension()
print(f"Modelo carregado. Tamanho do vetor: {VECTOR_SIZE}")

# ─────────────────────────────────────────────
# CONECTAR AO QDRANT
# ─────────────────────────────────────────────

print("\nConectando ao Qdrant...")
qdrant_client = QdrantClient(url=QDRANT_URL)
print("Conexão com Qdrant OK.")

# ─────────────────────────────────────────────
# CRIAR COLEÇÃO
# ─────────────────────────────────────────────

existing = [c.name for c in qdrant_client.get_collections().collections]
if COLLECTION_NAME in existing:
    print(f"Coleção '{COLLECTION_NAME}' já existe. Pulando indexação.")
    already_indexed = True
else:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE,
        ),
    )
    print(f"Coleção '{COLLECTION_NAME}' criada.")
    already_indexed = False

# ─────────────────────────────────────────────
# INDEXAR FILMES NO QDRANT
# ─────────────────────────────────────────────

if not already_indexed:
    print("\nIndexando filmes no Qdrant...")
    total = len(df)
    for start in tqdm(range(0, total, BATCH_SIZE), desc="Enviando lotes"):
        end = min(start + BATCH_SIZE, total)
        batch = df.iloc[start:end]
        texts = batch["rag_text"].tolist()
        vectors = embedding_model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        points = []
        for i, (_, row) in enumerate(batch.iterrows()):
            points.append(models.PointStruct(
                id=start + i,
                vector=vectors[i].tolist(),
                payload={
                    "rag_text": row["rag_text"],
                    "title": str(row.get("Title", "")),
                    "year": str(row.get("Release Year", "")),
                    "genre": str(row.get("Genre", "")),
                    "director": str(row.get("Director", "")),
                    "plot": str(row.get("Plot", "")),
                }
            ))
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("Indexação concluída.")

# ─────────────────────────────────────────────
# CLIENTE MARITACA
# ─────────────────────────────────────────────

maritaca_client = OpenAI(
    api_key=MARITACA_API_KEY,
    base_url=MARITACA_BASE_URL,
)
print("\nCliente da Maritaca criado.")

# ─────────────────────────────────────────────
# FUNÇÕES HYDE RAG
# ─────────────────────────────────────────────

def generate_hypothetical_document(question):
    """
    ETAPA HYDE: pede para a Maritaca gerar um filme hipotético
    que responderia a pergunta. Esse texto hipotético será embedado
    e usado para buscar filmes reais no Qdrant.
    """
    prompt = (
        f"Imagine um filme que responderia perfeitamente à seguinte pergunta: '{question}'. "
        f"Escreva uma breve sinopse desse filme hipotético em inglês, "
        f"incluindo título, gênero, diretor fictício e plot resumido. "
        f"Seja conciso, máximo 100 palavras."
    )
    response = maritaca_client.chat.completions.create(
        model=MARITACA_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def search_by_hypothetical(hypothetical_doc, top_k=TOP_K):
    """Embeda o documento hipotético e busca filmes reais similares."""
    vector = embedding_model.encode(
        hypothetical_doc,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    try:
        result = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=top_k,
            with_payload=True,
        )
        return result.points
    except AttributeError:
        return qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
        )


def build_context(results):
    blocks = []
    for i, point in enumerate(results, 1):
        p = point.payload
        blocks.append(
            f"[Filme {i} | Similaridade: {point.score:.4f}]\n"
            f"{p.get('rag_text', '')}"
        )
    return "\n\n---\n\n".join(blocks)


def ask_maritaca(question, context):
    system = (
        "Você é um assistente especializado em filmes. "
        "Responda em português do Brasil. "
        "Use somente o contexto fornecido. "
        "Se não encontrar informação suficiente, diga isso claramente."
    )
    user = (
        f"CONTEXTO RECUPERADO:\n{context}\n\n"
        f"PERGUNTA: {question}\n\n"
        f"Responda usando apenas o contexto acima."
    )
    response = maritaca_client.chat.completions.create(
        model=MARITACA_MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=500,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def hyde_rag(question, show_steps=True):
    """Fluxo completo do HyDE RAG."""
    if show_steps:
        print(f"\nPergunta: {question}")
        print("\n[HYDE] Gerando documento hipotético...")

    # Etapa 1: gerar documento hipotético
    hypothetical = generate_hypothetical_document(question)

    if show_steps:
        print(f"Documento hipotético gerado:\n{hypothetical}")
        print("\n[QDRANT] Buscando filmes reais similares...")

    # Etapa 2: buscar filmes reais com base no documento hipotético
    results = search_by_hypothetical(hypothetical)

    if show_steps:
        print("Filmes recuperados:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.payload.get('title')} | Score: {r.score:.4f}")
        print("\n[MARITACA] Gerando resposta final...")

    # Etapa 3: gerar resposta com contexto real
    context = build_context(results)
    answer = ask_maritaca(question, context)

    return answer


# ─────────────────────────────────────────────
# LOOP DE PERGUNTAS
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("HyDE RAG - Wikipedia Movie Plots")
print("Digite sua pergunta ou 'sair' para encerrar.")
print("="*60)

while True:
    question = input("\nPergunta: ").strip()
    if question.lower() in ["sair", "exit", "quit"]:
        print("Encerrando. Até mais!")
        break
    if not question:
        print("Digite uma pergunta válida.")
        continue

    answer = hyde_rag(question)
    print("\nResposta:")
    print("="*60)
    print(answer)
    print("="*60)