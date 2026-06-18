# Pipeline RAG Avançado com Re-ranqueamento por Cross-Encoder

Este repositório contém uma implementação estruturada, célula por célula, de um pipeline RAG (Geração Aumentada por Recuperação) avançado, otimizado para Google Colab ou Jupyter Notebooks locais. O pipeline melhora a precisão da busca vetorial tradicional ao incorporar uma etapa de re-ranqueamento semântico utilizando um modelo Cross-Encoder.

## Funcionalidades

- Divisão inteligente de texto com `RecursiveCharacterTextSplitter`.
- Estruturação de documentos com metadados personalizados.
- Indexação em banco de dados vetorial e busca por similaridade com ChromaDB e embeddings HuggingFace (`all-MiniLM-L6-v2`).
- Otimização de contexto com modelo Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) para eliminar resultados irrelevantes (ruído).
- Síntese automatizada do prompt final para Modelos de Linguagem de Grande Escala (LLMs).

## Requisitos

- `langchain`
- `sentence-transformers`
- `chromadb`
- `langchain-community`

## Estrutura do Projeto

1. **Célula 1: Configuração do Ambiente** — Instala todas as dependências necessárias.
2. **Célula 2: Importações e Configurações** — Inicializa o divisor de texto recursivo com separadores, tamanho de chunk e sobreposição configurados.
3. **Célula 3: Processamento e Vetorização de Documentos** — Define a base de conhecimento, anexa metadados, gera embeddings semânticos e os armazena no banco vetorial Chroma.
4. **Célula 4: Recuperação e Re-ranqueamento** — Executa a busca por similaridade inicial, calcula os scores de relevância via Cross-Encoder e filtra os contextos menos relevantes.
5. **Célula 5: Geração do Prompt** — Formata o contexto refinado e a pergunta do usuário em um prompt estruturado pronto para consumo pelo LLM.

## Como Usar

1. Abra um novo notebook no Google Colab ou no seu ambiente local.
2. Copie e cole o conteúdo de cada célula sequencialmente.
3. Execute as células em ordem para observar como o texto bruto se transforma em um contexto de prompt altamente refinado.
