from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool, Tool
from langchain_fireworks import ChatFireworks

from apic_agent.apic_client import APICClient
from apic_agent.langchain_agent import get_apic, get_uri, python_repl


client = APICClient()
model = ChatFireworks(model="accounts/fireworks/models/deepseek-v3", api_key=client.api_key)

tools  = [get_apic, get_uri, python_repl]

prompt = hub.pull("hwchase17/react")
langgraph_agent_executor = create_react_agent(model, tools, prompt=prompt)

template = """
    Role Definition:
    You are an intelligent assistant designed to support users interacting with the ACI (Application Centric Infrastructure) tool. Your primary objective is to assist users in resolving their queries related to the ACI tool by providing accurate and actionable responses.

    Guidelines for Tool interaction:

    1. get_uri
        Always use get_uri to export the correct uri
        Avoid using abbreviated or short-form inputs when calling the get_uri function. Instead, use fully descriptive terms.
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

"""
prompt_template = PromptTemplate.from_template(template)

agent = AgentExecutor(
    model=model,
    tools=tools,
    agent=langgraph_agent_executor,
    template=prompt_template,
    verbose=True,
    max_iterations=5
)

if __name__ == "__main__":
    query = "Check BDs"
    agent.invoke({"input": query})