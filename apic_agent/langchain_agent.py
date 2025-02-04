import json
import requests
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool, render_text_description
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_react_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from apic_client import APICClient
from langchain import hub

# Load URLs from a JSON file
def load_urls(file_path: str) -> dict:
    """Load URLs from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            urls = json.load(f)
        return urls
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return {}

# Tool: Fetch data from ACI controller
@tool
def get_aci_data_tool(api_url: str, apic_client: APICClient) -> str:
    """Fetch data from ACI controller."""
    try:
        apic_client._authenticate()
        # Return login successfully if okay
        if not apic_client.cookie:
            return {"error": "Failed to authenticate with APIC."}
        data = apic_client.get_resource(api_url)
        return data
    except requests.HTTPError as e:
        return {"error": f"Failed to fetch data from ACI: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Tool: Execute Python code in a REPL
@tool
def python_repl_tool(code: str) -> str:
    """Execute Python code in a REPL."""
    try:
        repl = PythonREPLTool()
        return repl.run(code)
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Get response from the agent
def get_response(agent_executor, question: str):
    """Get response from the agent."""
    response = agent_executor.invoke({
        "input": question
    })
    return response

apic_client = APICClient()

# Initialize the APIC client
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=apic_client.api_key,
    temperature=0
)

# Load URLs
urls = load_urls('/home/dsu979/Documents/AI_Agents/APIC_Agent/apic_agent/urls.json')


# Render tool descriptions and names
tools = [get_aci_data_tool, python_repl_tool]

# Define the prompt template
template = '''
Assistant is a network assistant with the capability to manage data from Cisco ACI controllers using CRUD operations.
NETWORK INSTRUCTIONS:
Assistant is designed to retrieve, create, update, and delete information from the Cisco ACI controller using provided tools. You MUST use these tools for checking available data, fetching it, creating new data, updating existing data, or deleting data.
Assistant has access to a list of API URLs and their associated Names provided in a 'urls.json' file. You can use the 'Name' field to find the appropriate API URL to use. For APIC_IP, It must 192.168.1.250
**Important Guidelines:**
1. **Use the 'get_aci_data_tool' to view all available data.**
2. **Use the Python REPL tool to execute Python code in case you need ajust to readablity of the data.**

**Using the tools:**
- If you are confident with the data, you can use the 'get_aci_data_tool' to view all available data.
- If you need to adjust the data, you can use the Python REPL tool to execute Python code.
To use a tool, follow this format:
Thought: Do I need to use a tool? Yes
Action: the action to take
Action Input: the input to the action
Observation: the result of the action

Question: {input}
"""

'''

# Create the prompt template
prompt_template = PromptTemplate.from_template(template)

# Pull the react prompt from the hub
prompt = hub.pull('hwchase17/react')


# Create the agent
agent = create_react_agent(llm, tools, prompt)

# Create the AgentExecutor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10
)

if __name__ == '__main__':
    print("Welcome to the Cisco ACI Agent!")
    questions = "Check current tenant"

    output = agent_executor.invoke({
        'input': prompt_template.format(input=questions)
    })