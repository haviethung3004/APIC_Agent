from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool, Tool
# from langchain_fireworks import ChatNvidia
# from langchain_deepseek import ChatDeepSeek
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from agent.apic_client import APICClient
from agent.agent_rest_tool import get_apic
from agent.agent_rag_tool import query_and_retrieve_document


client = APICClient()
model = ChatOpenAI(model="qwen-plus", api_key=client.api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")

tools  = [get_apic, query_and_retrieve_document]

prompt = hub.pull("hwchase17/react")
langgraph_agent_executor = create_react_agent(model, tools, prompt=prompt)

template = """
Role Definition:
You are an intelligent assistant designed to help users interact with the Cisco ACI (Application Centric Infrastructure) REST API. 
Your primary goal is to assist users in retrieving accurate information related to ACI resources by leveraging the provided tools.

Instructions:
1. **Step 1: Use the `query_and_retrieve_document` Tool**
   - This tool helps you retrieve the correct URL from the ACI REST API.
   - Your input for this tool must begin with: "Please share URL only, [your input here]".
   - Ensure that your query makes sense when using the `query_and_retrieve_document` tool.
   - **If you fail to retrieve a valid URL, 
   please retry and ask the `query_and_retrieve_document` agent with the other question to ensure you get the correct URL. 
   You should share wrong URL to the `query_and_retrieve_document` agent to let he know it wrong and share the other url. This URL should provides the JSON format**
    - Example:
     - User asks: "How many tenants are on the fabric?"
     - You should ask the `query_and_retrieve_document` with the input: "Please share URL only, how can we check the tenants on the fabric?"
     - `query_and_retrieve_document`: "https://apic-ip-address/api/class/fvTenant.json?subscription=yes"
     - You checked and see the uri wrong or not allowed, ask `query_and_retrieve_document` again: "The url https://apic-ip-address/api/class/fvTenant.json?subscription=yes for get tenant information was wrong. Can you share me the other url for checking tenants on the fabric?"


2. **Step 2: Use the `get_apic` Tool**
   - After retrieving the valid URL from Step 1, use the `get_apic` tool to fetch the actual information from the ACI REST API.
   - Your input for this tool must begin with: "/api/.....".
   - Example:
     - If the URL retrieved from Step 1 is `/api/mo/uni/tn.json`, you should use the tool with the input: `/api/mo/uni/tn.json`.

Question:
{q}

"""


prompt_template = PromptTemplate.from_template(template)

agent = AgentExecutor(
    model=model,
    tools=tools,
    agent=langgraph_agent_executor,
    verbose=True,
    max_iterations=10
)


#----------------------------------------------------------
#----------------- Streamlit Application ------------------
#----------------------------------------------------------
import streamlit as st
from dotenv import set_key, load_dotenv
import os

# Function to save APIC credentials to a .env file
def save_to_env(apic_ip, username, password):
    """Save APIC credentials to a .env file."""
    set_key(".env", "APIC_BASE_URL", apic_ip)
    set_key(".env", "APIC_USERNAME", username)
    set_key(".env", "APIC_PASSWORD", password)
    st.success("✅ Credentials saved successfully to `.env` file!")

# Main function for the Streamlit app
def main():
    # Load .env file if it exists
    load_dotenv()

    # Set up the Streamlit app title and description
    st.title("🌐 APIC Agent")
    st.markdown("""
    Welcome to the **APIC Agent**, an intelligent assistant for interacting with Cisco's Application Centric Infrastructure (ACI) tool.
    You can query tenant information, check bridge domains, execute Python code, and more!
    """)
    st.markdown("---")

    # Sidebar for APIC credentials
    st.sidebar.header("🔑 APIC Credentials")
    apic_ip = st.sidebar.text_input(
        "APIC IP/URL", 
        value=os.getenv("APIC_BASE_URL", ""), 
        key="apic_ip", 
        placeholder="e.g., https://192.168.1.250"
    )
    username = st.sidebar.text_input(
        "Username", 
        value=os.getenv("APIC_USERNAME", ""), 
        key="username", 
        placeholder="e.g., admin"
    )
    password = st.sidebar.text_input(
        "Password", 
        value=os.getenv("APIC_PASSWORD", ""), 
        type="password", 
        key="password", 
        placeholder="Enter your password"
    )

    # Button to save credentials to .env file
    if st.sidebar.button("💾 Save Credentials"):
        if apic_ip.strip() == "" or username.strip() == "" or password.strip() == "":
            st.sidebar.warning("⚠️ Please fill in all fields.")
        else:
            save_to_env(apic_ip, username, password)

    # Input field for user query
    st.subheader("📝 Query Section")
    query = st.text_area(
        "Enter your query here:", 
        height=150, 
        placeholder="Type your query..."
    )

    # Button to execute the query
    if st.button("🚀 Run Query"):
        if query.strip() == "":
            st.warning("⚠️ Please enter a query.")
        else:
            # Simulate agent invocation
            with st.spinner("⏳ Processing your query..."):
                try:
                    response = agent.invoke({"input": prompt_template.format(q=query)})
                    output = response.get("output", "No response received.")
                    st.success("✅ Query executed successfully!")
                    st.subheader("🔍 Response:")
                    st.write(output)
                    #st.code(output, language="plaintext")  # Display response in a code block
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    main()