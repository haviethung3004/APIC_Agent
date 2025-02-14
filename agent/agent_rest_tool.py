from agent.apic_client import APICClient
from langchain_fireworks import ChatFireworks
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

# Import the Langgraph and create_react_agent
# from langgraph.prebuilt import create_react_agent
# Import the process function from the fuzzywuzzy module (For finding the closest uri match)
import json
client = APICClient()
# model = ChatFireworks(model="accounts/fireworks/models/deepseek-v3", api_key=client.api_key)


# Define the python_repl tool
@tool
def python_repl(input: str) -> str:
    """
    This tool executes valid Python code and returns the output.
    The input must be a valid Python expression or statement.
    """
    # Create an instance of PythonREPL
    repl = PythonREPL()

    # Sanitize the input to remove unwanted characters
    sanitized_input = PythonREPL.sanitize_input(input)

    try:
        # Execute the sanitized input using the PythonREPL instance
        output = repl.run(sanitized_input)
        return output
    except Exception as e:
        # Return the error message if execution fails
        return f"Error executing Python code: {str(e)}"

    

@tool
def get_apic(uri: str) -> json:
    """
    This tool calls the APIC GET method and get information from the APIC.
    """
    response = client.get_resource(uri)
    return response


@tool
def post_apic(uri: str, payload: dict) -> str:
    """
    This tool calls the APIC POST method to change configuration on APIC.
    """
    response = client.post_resouce(uri, payload)

    return response

if __name__ == "__main__":

    pass


    
