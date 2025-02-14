from langchain_unstructured import UnstructuredLoader
# from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import pinecone
# Chat history in langchain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder

from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import tool
import os
import time

#Load the environment variables
load_dotenv(find_dotenv(), override=True)


#-------------------------------------------------------
#-------------Spliting and Chunking the PDF-------------
#-------------------------------------------------------
def load_pdf_pages(file_path: list[str]):
    """
    Synchronously loads and splits a PDF file into pages.
  
    Parameters:
        file_path (str): The path to the PDF file.
    
    Returns:
        docs: A list of document objects (each representing a page) loaded via UnstructuredLoader.
    """
    loader = UnstructuredLoader(
    file_path=file_path,
    api_key=os.getenv("UNSTRUCTURED_API_KEY"),
    partition_via_api=True
    )
    docs = loader.load()  # Synchronous loading
    return docs



#-----------------------------------------------------------
#-Embedding and Saving it to Vector Store in Pinecone-------
#-----------------------------------------------------------
def embedding_and_saving(index_name, docs):
    """
    Creates embeddings for the provided documents and saves them to a Pinecone vector store.
  
    Parameters:
        index_name: The name of the Pinecone index.
        docs: The list of documents to be embedded and stored.
    
    Returns:
        vector_store: An instance of the PineconeVectorStore with documents added.
    """
    #Create a embedding model using Google Generative AI
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GEMINI_API_KEY"))

    #Create a Pinecone Vector Store instance
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws", 
                region="us-east-1"
            ) 
        ) 

    # Wait for the index to be ready
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

    vector_store = PineconeVectorStore(index=index_name, embedding=embeddings)
    #Embed and save the documents to the vector store
    vector_store.add_documents(documents=docs)

    return vector_store

#-------------------------------------------------------
#------------QUERY AND RETRIVE DOCUMENT------------------
#-------------------------------------------------------

@tool
def query_and_retrieve_document(query: str):
    """
    Performs a similarity search on the Pinecone vector store and uses the retrieved context
    to generate an answer via a language model.
  
    Parameters:
        query (str): The user's query to search in the vector store.
    
    Returns:
        The content of the generated answer from the language model.
        Returns None if an error occurs.
    """

    #Check Index Name on Pinecone Database with your actual index name
    index_name="rest-apic-configuration"
    #Create a embedding model using Google Generative AI and vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GEMINI_API_KEY"))
    vector_store = PineconeVectorStore(index_name=index_name,embedding=embeddings, pinecone_api_key=os.getenv("PINECONE_API_KEY"))

    try:
        retrieved_docs = vector_store.similarity_search(query=query, k=10)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        #Define the prompt template
        from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
        from langchain_openai import ChatOpenAI
        from agent.apic_client import APICClient

        client = APICClient()
        llm = ChatOpenAI(model="qwen-plus", api_key=client.api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")

        prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            You are an expert AI assistant that helps users answer questions based on provided context.
            Use the following pieces of retrieved context to answer the question. 
            Based on the context provided, you need to learn and reply as best as you can.
            If you don't know the answer, Must not answer if you don't know the answer.
            Use three sentences maximum and keep the answer concise.
            Always provide a approriate url
            
            Question: {question}
            Context: {context}
            
            Answer:

            """
        )

        # Format the prompt
        formatted_prompt = prompt_template.format(question=query, context=docs_content)

        # Generate the answer using the LLM
        answer = llm.invoke(formatted_prompt)
        return answer.content
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # file_path = "/home/dsu979/Documents/AI_Agents/APIC_Agent/agent/content/docs/cisco-apic-rest-api-configuration-guide-42x-and-later.pdf"
    #Load the pages from the PDF

    respones = query_and_retrieve_document("How can get tenant information using REST API?")
    print(respones)