# LangChain

> **TL;DR** — LangChain is a Python/TypeScript framework that provides composable building blocks (chains, retrievers, agents, document loaders) for building LLM applications; it dramatically reduces the boilerplate of connecting embeddings, vector stores, and LLMs.

## Overview

LangChain abstracts away the repetitive code needed to wire together an LLM pipeline. Key abstractions include **Document Loaders**, **Text Splitters**, **Embedding models**, **Vector Stores**, **Retrievers**, and **Chains**. These can be composed into pipelines that are readable and testable.

## Core Abstractions

| Abstraction | Purpose |
|---|---|
| `Document` | A chunk of text + metadata dict |
| `DocumentLoader` | Reads files, URLs, databases into `Document` objects |
| `TextSplitter` | Splits long documents into chunks |
| `Embeddings` | Interface to an embedding model |
| `VectorStore` | Interface to a vector database |
| `Retriever` | Wraps a VectorStore; exposes `.get_relevant_documents(query)` |
| `Chain` | Combines retrievers, prompts, and LLMs into a pipeline |
| `ChatModel` | Interface to a chat-based LLM |

## Installation

```bash
pip install langchain langchain-openai langchain-qdrant langchain-community
```

## Document Loading and Splitting

```python
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load all markdown files from a directory
loader = DirectoryLoader("docs/", glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
chunks = splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks from {len(docs)} documents")
```

## Indexing into Qdrant

```python
from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)

vectorstore = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="wiki",
)
```

## Building a RetrievalQA Chain

```python
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

PROMPT_TEMPLATE = """Use ONLY the following context to answer the question.
If the answer is not in the context, say "I don't know."

Context:
{context}

Question: {question}
Answer:"""

prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])

llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01",
    temperature=0,
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True,
)

result = qa_chain.invoke("What is the purpose of a Kubernetes HorizontalPodAutoscaler?")
print(result["result"])
print("\nSources:")
for doc in result["source_documents"]:
    print(" -", doc.metadata.get("source", "unknown"))
```

## LCEL (LangChain Expression Language)

Modern LangChain recommends **LCEL** — a declarative syntax using `|` pipes:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template("""Answer based on context only:
Context: {context}
Question: {question}""")

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    {"context": vectorstore.as_retriever() | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print(chain.invoke("Explain pod scheduling in Kubernetes"))
```

## Trade-offs / Considerations

- **Abstraction overhead**: LangChain hides complexity but can make debugging harder. Log intermediate steps with `verbose=True` or LangSmith tracing.
- **Version churn**: LangChain has changed its API significantly between versions. Pin versions in `requirements.txt`.
- **Alternative frameworks**: LlamaIndex, Haystack, DSPy — each has trade-offs. LangChain has the largest ecosystem.

## References

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangChain LCEL Guide](https://python.langchain.com/docs/expression_language/)
- Source: [RAG Workshop — DevOpsDay 2025](../../content/posts/2025-06-06-devops-rag-internal-ai.md)
