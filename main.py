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
   - This tool helps you retrieve the correct URI from the ACI REST API.
   - Your input for this tool must begin with: "Please share uri only, [your input here]".
   - Example:
     - User asks: "How many tenants are on the fabric?"
     - You should use the tool with the input: "Please share uri only, how can we check the tenants on the fabric?"
   - Ensure that your query makes sense when using the `query_and_retrieve_document` tool.
   - **If you fail to retrieve a valid URI, 
   please retry and ask the `query_and_retrieve_document` agent with the other question to ensure you get the correct URI. 
   You can share wrong uri for the `query_and_retrieve_document` agent to get other uri or other way to get good result. This URI should provides the JSON format**
   

2. **Step 2: Use the `get_apic` Tool**
   - After retrieving the valid URI from Step 1, use the `get_apic` tool to fetch the actual information from the ACI REST API.
   - Your input for this tool must begin with: "/api/.....".
   - Example:
     - If the URI retrieved from Step 1 is `/api/mo/uni/tn.json`, you should use the tool with the input: `/api/mo/uni/tn.json`.

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

def main():
    # Set up the Streamlit app title and description
    st.title("APIC Agent")
    st.markdown("""
    Welcome to the **APIC Agent**, an intelligent assistant for interacting with Cisco's Application Centric Infrastructure (ACI) tool.
    You can query tenant information, check bridge domains, execute Python code, and more!
    """)

    # Input field for user query
    query = st.text_area("Enter your query here:", height=100)

    # Button to execute the query
    if st.button("Run Query"):
        if query.strip() == "":
            st.warning("Please enter a query.")
        else:
            # Run the agent with the user query
            with st.spinner("Processing your query..."):
                try:
                    response = agent.invoke({"input": prompt_template.format(q=query)})
                    output = response.get("output", "No response received.")
                    st.success("Query executed successfully!")
                    st.subheader("Response:")
                    st.write(output)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    main()