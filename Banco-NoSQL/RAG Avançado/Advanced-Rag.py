"""
RAG Avançado - Implementação Completa
Técnicas: Pré-recuperação, Pós-recuperação e Re-ranqueamento

Requisitos:
    pip install langchain langchain-community langchain-text-splitters langchain-core chromadb sentence-transformers ollama
"""

import os
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

USE_OPENAI = False

if USE_OPENAI:
    from langchain_openai import ChatOpenAI
    os.environ["OPENAI_API_KEY"] = "SUA_CHAVE_AQUI"
else:
    from langchain_community.llms import Ollama

DOCUMENTOS_EXEMPLO = [
    """
    Inteligência Artificial é um campo da ciência da computação que busca criar sistemas
    capazes de realizar tarefas que normalmente requerem inteligência humana. Inclui
    aprendizado de máquina, processamento de linguagem natural e visão computacional.
    """,
    """
    Machine Learning é um subcampo da IA onde os sistemas aprendem com dados sem serem
    explicitamente programados. Os principais tipos são: aprendizado supervisionado,
    não-supervisionado e por reforço.
    """,
    """
    RAG (Retrieval-Augmented Generation) combina recuperação de informações com geração
    de texto. O sistema busca documentos relevantes em uma base de conhecimento e os usa
    como contexto para que o LLM gere respostas mais precisas e atualizadas.
    """,
    """
    Modelos de linguagem grandes (LLMs) como GPT e LLaMA são treinados em enormes
    quantidades de texto. Eles geram texto de forma autoregressiva, prevendo o próximo
    token com base no contexto anterior.
    """,
    """
    Embeddings são representações vetoriais de texto em espaços de alta dimensionalidade.
    Textos semanticamente similares ficam próximos no espaço vetorial, permitindo
    buscas por similaridade semântica eficientes.
    """,
    """
    Bancos vetoriais como ChromaDB, Pinecone e Weaviate armazenam embeddings e permitem
    buscas por vizinhos mais próximos (k-NN). São fundamentais para sistemas RAG.
    """,
    """
    O re-ranqueamento (reranking) é uma técnica de pós-recuperação que reordena os
    documentos recuperados por relevância real à consulta do usuário, melhorando
    a qualidade do contexto enviado ao LLM.
    """,
    """
    Chunking é o processo de dividir documentos em pedaços menores para indexação.
    Estratégias incluem: por tamanho fixo, por parágrafo, por sentença ou de forma
    hierárquica (chunk pai/filho).
    """,
]


# ─────────────────────────────────────────────────────────────
# MÓDULO 1 — PRÉ-RECUPERAÇÃO
# ─────────────────────────────────────────────────────────────

class PreRecuperacao:
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " "],
        )

    def processar_documentos(self, textos: List[str]) -> List[Document]:
        documentos = []
        for i, texto in enumerate(textos):
            chunks = self.splitter.split_text(texto.strip())
            for j, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "fonte": f"documento_{i+1}",
                        "chunk_id": j,
                        "tamanho": len(chunk),
                    },
                )
                documentos.append(doc)
        print(f"[Pré-recuperação] {len(textos)} documentos → {len(documentos)} chunks gerados")
        return documentos

    def expandir_consulta(self, consulta: str, llm) -> List[str]:
        prompt = (
            "Gere 3 reformulações diferentes da seguinte pergunta para melhorar "
            "a busca em um sistema RAG. Retorne apenas as 3 perguntas, uma por linha, "
            "sem numeração nem prefixos.\n\n"
            f"Pergunta original: {consulta}"
        )
        try:
            if USE_OPENAI:
                resposta = llm.invoke(prompt).content
            else:
                resposta = llm.invoke(prompt)
            variacoes = [linha.strip() for linha in resposta.strip().split("\n") if linha.strip()]
            todas = [consulta] + variacoes[:3]
            print(f"[Pré-recuperação] Query expandida: {len(todas)} variações geradas")
            return todas
        except Exception as e:
            print(f"[Pré-recuperação] Expansão falhou, usando consulta original. Erro: {e}")
            return [consulta]


# ─────────────────────────────────────────────────────────────
# MÓDULO 2 — RE-RANQUEAMENTO
# ─────────────────────────────────────────────────────────────

class ReRanqueador:
    def __init__(self, modelo_embeddings):
        self.embeddings = modelo_embeddings

    def _cosseno(self, a: List[float], b: List[float]) -> float:
        import math
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x ** 2 for x in a))
        mag_b = math.sqrt(sum(x ** 2 for x in b))
        return dot / (mag_a * mag_b + 1e-9)

    def reranquear(self, consulta: str, documentos: List[Document], top_n: int = 3) -> List[Tuple[Document, float]]:
        emb_consulta = self.embeddings.embed_query(consulta)
        scored = []
        for doc in documentos:
            emb_doc = self.embeddings.embed_query(doc.page_content)
            score = self._cosseno(emb_consulta, emb_doc)
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_n]
        print(f"[Re-ranqueamento] {len(documentos)} chunks → top {top_n} selecionados")
        for doc, score in top:
            print(f"  Score {score:.4f} | {doc.page_content[:60]}...")
        return top


# ─────────────────────────────────────────────────────────────
# MÓDULO 3 — PÓS-RECUPERAÇÃO
# ─────────────────────────────────────────────────────────────

class PosRecuperacao:
    def __init__(self, score_minimo: float = 0.3, limiar_duplicata: float = 0.95):
        self.score_minimo = score_minimo
        self.limiar_duplicata = limiar_duplicata

    def filtrar_por_score(self, documentos_scored: List[Tuple[Document, float]]) -> List[Tuple[Document, float]]:
        filtrados = [(doc, score) for doc, score in documentos_scored if score >= self.score_minimo]
        print(f"[Pós-recuperação] Filtro de score ≥ {self.score_minimo}: {len(filtrados)} chunks mantidos")
        return filtrados

    def desduplicar(self, documentos_scored: List[Tuple[Document, float]]) -> List[Tuple[Document, float]]:
        vistos = set()
        unicos = []
        for doc, score in documentos_scored:
            chave = doc.page_content[:80].strip().lower()
            if chave not in vistos:
                vistos.add(chave)
                unicos.append((doc, score))
        print(f"[Pós-recuperação] Após deduplicação: {len(unicos)} chunks únicos")
        return unicos

    def montar_contexto(self, documentos_scored: List[Tuple[Document, float]]) -> str:
        partes = []
        for i, (doc, score) in enumerate(documentos_scored, 1):
            fonte = doc.metadata.get("fonte", "desconhecida")
            partes.append(f"[Trecho {i} | Fonte: {fonte} | Score: {score:.3f}]\n{doc.page_content}")
        return "\n\n---\n\n".join(partes)


# ─────────────────────────────────────────────────────────────
# PIPELINE RAG AVANÇADO COMPLETO
# ─────────────────────────────────────────────────────────────

class RAGAvancado:
    def __init__(self, top_k: int = 6, top_n: int = 3):
        self.top_k = top_k
        self.top_n = top_n

        print("Carregando modelo de embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        print("Inicializando LLM...")
        if USE_OPENAI:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        else:
            self.llm = Ollama(model="llama3", temperature=0)

        self.pre = PreRecuperacao(chunk_size=300, chunk_overlap=50)
        self.reranqueador = ReRanqueador(self.embeddings)
        self.pos = PosRecuperacao(score_minimo=0.2)
        self.vectorstore = None

    def indexar(self, textos: List[str]):
        documentos = self.pre.processar_documentos(textos)
        print("Criando banco vetorial ChromaDB...")
        self.vectorstore = Chroma.from_documents(
            documents=documentos,
            embedding=self.embeddings,
            collection_name="rag_avancado",
        )
        print(f"[Indexação] {len(documentos)} chunks indexados com sucesso.\n")

    def consultar(self, pergunta: str) -> str:
        if not self.vectorstore:
            raise RuntimeError("Execute indexar() antes de consultar().")

        print(f"\n{'='*60}")
        print(f"PERGUNTA: {pergunta}")
        print("=" * 60)

        consultas = self.pre.expandir_consulta(pergunta, self.llm)

        todos_chunks = []
        vistos = set()
        for q in consultas:
            resultados = self.vectorstore.similarity_search(q, k=self.top_k)
            for doc in resultados:
                chave = doc.page_content[:80].strip()
                if chave not in vistos:
                    vistos.add(chave)
                    todos_chunks.append(doc)
        print(f"[Recuperação] {len(todos_chunks)} chunks únicos após multi-query")

        top_scored = self.reranqueador.reranquear(pergunta, todos_chunks, top_n=self.top_n)
        top_scored = self.pos.filtrar_por_score(top_scored)
        top_scored = self.pos.desduplicar(top_scored)
        contexto = self.pos.montar_contexto(top_scored)

        template = PromptTemplate(
            input_variables=["contexto", "pergunta"],
            template=(
                "Você é um assistente especializado. Responda à pergunta usando apenas "
                "as informações do contexto abaixo. Se não houver informação suficiente, "
                "diga que não sabe.\n\n"
                "CONTEXTO:\n{contexto}\n\n"
                "PERGUNTA: {pergunta}\n\n"
                "RESPOSTA:"
            ),
        )
        prompt_final = template.format(contexto=contexto, pergunta=pergunta)

        print("\n[Geração] Enviando contexto refinado ao LLM...")
        if USE_OPENAI:
            resposta = self.llm.invoke(prompt_final).content
        else:
            resposta = self.llm.invoke(prompt_final)

        print("\n" + "=" * 60)
        print("RESPOSTA FINAL:")
        print("=" * 60)
        print(resposta)
        return resposta


if __name__ == "__main__":
    rag = RAGAvancado(top_k=6, top_n=3)
    rag.indexar(DOCUMENTOS_EXEMPLO)

    perguntas = [
        "O que é RAG e como ele funciona?",
        "Qual a diferença entre embeddings e chunking?",
        "Para que serve o re-ranqueamento em sistemas RAG?",
    ]

    for pergunta in perguntas:
        rag.consultar(pergunta)
        print("\n")