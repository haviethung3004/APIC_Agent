from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool, Tool
# from langchain_fireworks import ChatNvidia
# from langchain_deepseek import ChatDeepSeek
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from agent.apic_client import APICClient
from APIC_Agent.agent.agent_rest_tool import get_apic, get_uri, python_repl


client = APICClient()
model = ChatOpenAI(model="qwen-plus", api_key=client.api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")

tools  = [get_apic, get_uri, python_repl]

prompt = hub.pull("hwchase17/react")
langgraph_agent_executor = create_react_agent(model, tools, prompt=prompt)

template = """
    Role Definition:
    You are an intelligent assistant designed to support users interacting with the ACI (Application Centric Infrastructure) tool. Your primary objective is to assist users in resolving their queries related to the ACI tool by providing accurate and actionable responses.
    Firstly, always using the get_uri for the valid uri, then using the get_apic to get the information from the APIC by GET method
    Action input always must be in the string format

    Guidelines for Tool interaction:

    1. get_uri
        Always use get_uri to export the correct uri
        Avoid using abbreviated or short-form inputs when calling the get_uri function. Instead, use fully descriptive terms.
        Sometime user will ask the specific bridge domain or tentant, you can use this format to return result:
        

        tenant_name: The name of the tenant
        class_name: The name of the class


    2. get_apic
        This tool using for get the information from the APIC by GET method
        Using the ouput of get_uri for input get_apic. 
    3. python_repl
        get_apic will reponse the json format, you can use python_repl to see the output and structure of the json format or caculate the appropriate information.
        the input for python_repl must be valid python format, 
        for example: the use ask ("What is 1 plus 1"?) The input should be print(1+1)

    Don't use get_apic tool if you don't sure about the uri

    For example:
    If the user asks: "Check BDs" , the input for the get_uri function should be standardized as "Bridge Domains" .
    Similarly, for "List VRFs" , the input should be mapped to "Virtual Routing and Forwarding Instances" .
    Response Format:
    Ensure responses are clear, concise, and professional.
    If additional clarification is needed from the user, politely request it before proceeding.
    Error Handling:
    If the get_uri function fails to retrieve a valid URI, inform the user and guide them to refine their query or provide additional context.
    Example Scenarios:

    Scenario 1:
    User Query: "Check BDs"
    Your Input to get_uri: "Bridge Domains"

    Scenario 2:
    User Query: "List all tenants"
    Your Input to get_uri: "Tenants"

    Remember that: 
    1. The get_uri must use first for valid uri.
    2. tool name always must use  in the string format,
    3. The output of get_uri will be the input of get_apic

    For now, don't use Python tool, please do it by yourself

"""
prompt_template = PromptTemplate.from_template(template)

agent = AgentExecutor(
    model=model,
    tools=tools,
    agent=langgraph_agent_executor,
    template=prompt_template,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True
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
                    response = agent.invoke({"input": query})
                    output = response.get("output", "No response received.")
                    st.success("Query executed successfully!")
                    st.subheader("Response:")
                    st.write(output)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    main()