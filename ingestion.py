from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore

load_dotenv()

from langchain_community.document_loaders import ReadTheDocsLoader, FireCrawlLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeLangChain

INDEX_NAME = "langchain-doc-index"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def ingest_docs():
    loader = ReadTheDocsLoader(
        "langchain-docs/api.python.langchain.com/en/latest"
    )

    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    documents = text_splitter.split_documents(raw_documents)
    for doc in documents:
        new_url = doc.metadata["source"]
        new_url = new_url.replace("langchain-docs", "https:/")
        doc.metadata.update({"source": new_url})

    print(f"Going to add {len(documents)} to Pinecone")
    PineconeLangChain.from_documents(documents, embeddings, index_name=INDEX_NAME)
    print("****Loading to vectorstore done ***")

def ingest_docs2():

    langchain_documents_base_urls = [
        "https://python.langchain.com/docs/integrations/chat/",
        "https://python.langchain.com/docs/integrations/llms/",
        "https://python.langchain.com/docs/integrations/retrievers/",
        "https://python.langchain.com/docs/integrations/document_loaders/",
        "https://python.langchain.com/docs/integrations/vectorstores/",
        "https://python.langchain.com/docs/integrations/text_embedding/",
        "https://python.langchain.com/docs/integrations/document_transformers/"
    ]
    langchain_documents_base_urls2 = [langchain_documents_base_urls[0]]

    for url in langchain_documents_base_urls2:
        print(f"FireCrawling {url=}")
        loader = FireCrawlLoader(
            url=url,
            mode="scrape",
        )
        docs = loader.load()

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        print(f"Going to add {len(docs)} documents to Pinecone")
        PineconeVectorStore.from_documents(
            docs, embeddings, index_name="firecrawl-index"
        )

        print(f"***Loading {url}* to vectorstore done ***")


if __name__ == "__main__":
    ingest_docs2()
