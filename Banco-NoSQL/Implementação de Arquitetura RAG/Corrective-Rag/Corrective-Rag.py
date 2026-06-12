import os
import pandas as pd
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
COLLECTION_NAME = "wiki_movies_corrective"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MARITACA_MODEL_NAME = "sabiazinho-4"
MARITACA_BASE_URL = "https://chat.maritaca.ai/api"
TOP_K = 5
BATCH_SIZE = 64
MAX_ROWS = 2000

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
# FUNÇÕES CORRECTIVE RAG
# ─────────────────────────────────────────────

def search_qdrant(query_text, top_k=TOP_K):
    """Busca filmes no Qdrant com base em um texto."""
    vector = embedding_model.encode(
        query_text,
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


def evaluate_relevance(question, results):
    """
    ETAPA CORRECTIVE: pede pra Maritaca avaliar se os resultados
    recuperados são relevantes para a pergunta.
    Retorna 'relevant', 'partially_relevant' ou 'irrelevant'.
    """
    context_preview = "\n".join([
        f"- {r.payload.get('title', '')} ({r.payload.get('year', '')}): {r.payload.get('plot', '')[:150]}..."
        for r in results
    ])

    prompt = (
        f"Você recebeu a seguinte pergunta sobre filmes: '{question}'\n\n"
        f"E os seguintes filmes foram recuperados de um banco de dados:\n{context_preview}\n\n"
        f"Avalie se esses filmes são relevantes para responder a pergunta.\n"
        f"Responda APENAS com uma das três opções:\n"
        f"- 'relevant' se os filmes são claramente relevantes\n"
        f"- 'partially_relevant' se os filmes têm alguma relação mas não são ideais\n"
        f"- 'irrelevant' se os filmes não têm relação com a pergunta\n"
        f"Responda somente com uma dessas palavras, sem explicação."
    )

    response = maritaca_client.chat.completions.create(
        model=MARITACA_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0.0,
    )
    verdict = response.choices[0].message.content.strip().lower()

    # normaliza a resposta
    if "irrelevant" in verdict:
        return "irrelevant"
    elif "partially" in verdict:
        return "partially_relevant"
    else:
        return "relevant"


def rewrite_query(question):
    """
    ETAPA CORRECTIVE: se os resultados forem irrelevantes,
    pede pra Maritaca reformular a pergunta para melhorar a busca.
    """
    prompt = (
        f"A seguinte pergunta não encontrou bons resultados em uma busca por filmes: '{question}'\n\n"
        f"Reescreva essa pergunta de forma diferente, usando outras palavras e termos em inglês, "
        f"para tentar encontrar filmes mais relevantes.\n"
        f"Responda apenas com a pergunta reformulada, sem explicação."
    )

    response = maritaca_client.chat.completions.create(
        model=MARITACA_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def build_context(results):
    """Monta o contexto com os filmes recuperados."""
    blocks = []
    for i, point in enumerate(results, 1):
        p = point.payload
        blocks.append(
            f"[Filme {i} | Similaridade: {point.score:.4f}]\n"
            f"{p.get('rag_text', '')}"
        )
    return "\n\n---\n\n".join(blocks)


def ask_maritaca(question, context):
    """Gera a resposta final com base no contexto recuperado."""
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


def corrective_rag(question, show_steps=True):
    """
    Fluxo completo do Corrective RAG:
    1. Busca inicial no Qdrant
    2. Avalia relevância dos resultados
    3. Se irrelevante: reformula a pergunta e busca de novo
    4. Gera resposta final com o melhor contexto encontrado
    """
    if show_steps:
        print(f"\nPergunta: {question}")
        print("\n[QDRANT] Busca inicial...")

    # Etapa 1: busca inicial
    results = search_qdrant(question)

    if show_steps:
        print("Filmes recuperados:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.payload.get('title')} | Score: {r.score:.4f}")
        print("\n[CORRECTIVE] Avaliando relevância...")

    # Etapa 2: avaliar relevância
    verdict = evaluate_relevance(question, results)

    if show_steps:
        print(f"Veredicto: {verdict}")

    # Etapa 3: corrigir se necessário
    if verdict == "irrelevant":
        if show_steps:
            print("\n[CORRECTIVE] Resultados irrelevantes! Reformulando pergunta...")

        rewritten = rewrite_query(question)

        if show_steps:
            print(f"Pergunta reformulada: {rewritten}")
            print("\n[QDRANT] Nova busca com pergunta reformulada...")

        results = search_qdrant(rewritten)

        if show_steps:
            print("Novos filmes recuperados:")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r.payload.get('title')} | Score: {r.score:.4f}")

    elif verdict == "partially_relevant":
        if show_steps:
            print("\n[CORRECTIVE] Resultados parciais. Expandindo busca...")

        rewritten = rewrite_query(question)
        extra_results = search_qdrant(rewritten)

        # combina os resultados originais com os novos, sem duplicatas
        seen = {r.payload.get('title') for r in results}
        for r in extra_results:
            if r.payload.get('title') not in seen:
                results.append(r)
                seen.add(r.payload.get('title'))

        results = results[:TOP_K]

        if show_steps:
            print("Filmes após expansão:")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r.payload.get('title')} | Score: {r.score:.4f}")

    # Etapa 4: gerar resposta final
    if show_steps:
        print("\n[MARITACA] Gerando resposta final...")

    context = build_context(results)
    answer = ask_maritaca(question, context)

    return answer, verdict


# ─────────────────────────────────────────────
# LOOP DE PERGUNTAS
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("Corrective RAG - Wikipedia Movie Plots")
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

    answer, verdict = corrective_rag(question)
    print("\nResposta:")
    print("="*60)
    print(answer)
    print(f"\n[Veredicto da busca: {verdict}]")
    print("="*60)