# Advanced RAG Pipeline with Cross-Encoder Re-ranking

This repository contains a structured, cell-by-cell implementation of an advanced Retrieval-Augmented Generation (RAG) pipeline optimized for Google Colab or local Jupyter Notebooks. The pipeline enhances traditional vector search accuracy by incorporating a semantic re-ranking step using a Cross-Encoder model.

## Features

- Intelligent text chunking using `RecursiveCharacterTextSplitter`.
- Document structuring with custom metadata.
- Vector database indexing and similarity search using ChromaDB and HuggingFace embeddings (`all-MiniLM-L6-v2`).
- Context optimization using a Cross-Encoder model (`ms-marco-MiniLM-L-6-v2`) to eliminate irrelevant search results (noise).
- Automated final prompt synthesis for Large Language Models (LLMs).

## Requirements

The implementation relies on the following libraries:
- `langchain`
- `sentence-transformers`
- `chromadb`
- `langchain-community`

## Project Structure

The codebase is split into modular execution cells:

1. **Cell 1: Environment Setup** - Installs all necessary dependencies in quiet mode.
2. **Cell 2: Core Imports and Configurations** - Initializes the recursive text splitter with tailored character separators, chunk size, and overlap parameters.
3. **Cell 3: Document Processing and Vectorization** - Defines the raw knowledge base, attaches relevant metadata, generates semantic embeddings, and stores them in an in-memory Chroma vector store.
4. **Cell 4: Retrieval and Re-ranking (Rerank)** - Executes the initial similarity search, computes exact question-document relevance scores via the Cross-Encoder, and filters out suboptimal contexts.
5. **Cell 5: Prompt Generation** - Formats the refined context and user query into a structured prompt layout ready for LLM consumption.

## Usage

1. Open a new notebook in Google Colab or your local environment.
2. Copy and paste the contents of each cell sequentially.
3. Execute the cells in order to observe how the raw text transforms into a highly refined prompt context.
