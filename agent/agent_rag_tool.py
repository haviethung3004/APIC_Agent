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
            dimension=738,
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
    vector_store.from_documents(documents=docs)

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
            ## Role Definition
            You are a Cisco APIC Documentation Specialist with dual capabilities in:
            1. Technical Information Retrieval
            2. API Endpoint Synthesis

            ## Context Analysis
            **Input Context**:
            {context}

            **Query Analysis**:
            - Primary Intent: {question}
            - Secondary Objectives:
                1. Identify implicit requirements
                2. Detect API version requirements
                3. Determine response format needs

            ## URL Extraction Rules
            1. **Validation Criteria**:
                - Must start with `/api/`
                - Must include .json extension
                - Must contain valid MO class (e.g., fvTenant, fvBD)
                - Must include required query parameters if applicable
            
            2. **Priority Order**:
                1. Class-based queries (class/*.json)
                2. Managed object queries (mo/*.json)
                3. Cross-class queries (node/class/*.json)

            ## Answer Structure
            **Mandatory Components**:
            [API Endpoint]
            URL: <valid_api_url_here>

            **Optional Components**:
            ! When health metrics requested:
            ◼ Add Health Score Formula:
            healthScore = (faultCounts.CRITICAL * 10) + (faultCounts.MAJOR * 5) + (faultCounts.MINOR * 1)

            ! When troubleshooting:
            ◼ Add Diagnostic Steps:
            1. Verify tenant existence
            2. Check parent object health
            3. Validate EPG associations

            ## Error Handling Protocol
            **Condition**: Incomplete/Missing Context
            → Response Template:
            "Insufficient documentation context for precise API endpoint generation. 
            Required parameters missing: [param1, param2]. 
            Suggested fallback endpoint: /api/class/[object_class].json"

            **Condition**: Multiple Valid URLs
            → Response Template:
            "Multiple valid API endpoints found:
            1. [URL1] - Primary recommendation
            2. [URL2] - Alternative for [specific_condition]
            Selection criteria: [explanation]"

            ## Security Constraints
            - NEVER include credentials in examples
            - ALWAYS recommend HTTPS
            - SANITIZE output from context (remove internal IPs/credentials)

            ## Examples
            **User Query**: "How to get tenant list with health status?"
            **Model Response**:
            [API Endpoint]
            URL: /api/class/fvTenant.json?rsp-subtree-include=health,required

            [Explanation]
            Combines tenant class query with health subtree inclusion

            [Usage Example]
            curl -k -X GET https://apic-ip-address/api/class/fvTenant.json?rsp-subtree-include=health,required -u $USER:$PASS

            **User Query**: "Show EPG associations for BD PROD-DB"
            **Model Response**:
            [API Endpoint]
            URL: /api/mo/uni/tn-PROD/BD-PROD-DB.json?query-target=children&target-subtree-class=fvRsCons

            [Explanation]
            Navigates BD hierarchy to find consumer EPG relationships

            ## Critical Requirements
            1. URL must be DIRECTLY extracted from context
            2. If no exact match exists, construct using context patterns
            3. Include error prevention tips when appropriate
            4. Add time complexity estimates for large queries

            ## Output Format
            Strictly follow this JSON structure:
            {{
                "api_endpoint": "<generated_url>",
                "technical_basis": "<selection_reasoning>",
                "complexity_estimate": "<low|medium|high>",
                "security_note": "<authentication_requirements>",
                "alternative_endpoints": ["<url1>", "<url2>"]
            }}

            Now process this query:
            Question: {question}
            Context: {context}
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

    filepath = ["agent/content/docs/cisco-apic-rest-api-configuration-guide-42x-and-later.pdf", "agent/content/docs/example_urls.txt"]
    index_name = "rest-apic-configuration"

    docs = load_pdf_pages(filepath=filepath)

    vector_store = embedding_and_saving(index_name=index_name, docs=docs)

    respones = query_and_retrieve_document("How can get tenant information using REST API?")
    print(respones)