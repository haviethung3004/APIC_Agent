# from langchain_unstructured import UnstructuredLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv, find_dotenv
import os

#Load the environment variables
load_dotenv(find_dotenv(), override=True)


#-------------------------------------------------------
#-------------Spliting and Chunking the PDF-------------
#-------------------------------------------------------
def load_pdf_pages(file_path: str):
    """Synchronously load pages from a PDF file"""
    loader = PyPDFLoader(file_path)
    pages = loader.load()  # Synchronous loading
    return pages



#-------------------------------------------------------
#--------Embedding and Saving it to Vecto Store---------
#-------------------------------------------------------
def embedding_and_saving(pages):
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GEMINI_API_KEY"))

    vector_store = Chroma(
    collection_name="REST_API_CONFIG_GUIDE",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db"
    )

    vector_store.add_documents(pages)

    return vector_store

#-------------------------------------------------------
#---------------------TOOL DEFINITION--------------------
#-------------------------------------------------------
def create_rag_tool(vector_store):
    """Create a LangChain Tool for querying and retrieving documents"""
    from langchain_core.tools import Tool
    return Tool(
        name="DocumentRetriever",
        func=lambda query: query_and_retrieve_document(query, vector_store),
        description="Useful for querying and retrieving relevant documents based on a user question."
    )


#-------------------------------------------------------
#------------QUERY AND RETRIVE DOCUMET------------------
#-------------------------------------------------------

def query_and_retrieve_document(query: str, vector_store):
    """Query and retrieve documents from the vector store"""
    try:
        retrieved_docs = vector_store.similarity_search(query, k=5)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        #Define the prompt template
        from langchain_core.prompts import PromptTemplate
        from langchain_openai import ChatOpenAI
        from apic_client import APICClient

        client = APICClient()
        llm = ChatOpenAI(model="qwen-plus", api_key=client.api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")

        prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            You are an expert AI assistant that helps users answer questions based on provided context.
            Use the following pieces of retrieved context to answer the question. Based on the context provided, you need to learn and reply as best as you can.
            If you don't know the answer, Must not answer if you don't know the answer.
            Use three sentences maximum and keep the answer concise.
            
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
    file_path = "/home/dsu979/Documents/AI_Agents/APIC_Agent/agent/content/docs/cisco-apic-rest-api-configuration-guide-42x-and-later.pdf"

    # Step 1: Load PDF pages
    pages = load_pdf_pages(file_path)
    if not pages:
        print("No pages loaded. Exiting.")
        exit(1)
    
    # Step 2: Embed and save to vector store
    vector_store = embedding_and_saving(pages)
    if not vector_store:
        print("Failed to create vector store. Exiting.")
        exit(1)
    
    # Step 3: Query and retrieve documents
    query = "Share me the payload for example to authenticate APIC using REST API" 
    answer = query_and_retrieve_document(query, vector_store)
    if answer:
        print(f"Answer: {answer}")
    else:
        print("Failed to retrieve an answer.")