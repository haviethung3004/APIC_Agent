from langchain.prompts import PromptTemplate
from langchain import hub
from langchain.agents import Tool, AgentExecutor, initialize_agent, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_deepseek import ChatDeepSeek

# Load the .env file
import os
from dotenv import load_dotenv, find_dotenv

# loading the API Keys from .env
load_dotenv(find_dotenv(), override=True)

# Initialize the ChatOpenAI model
llm = ChatDeepSeek(
    model='deepseek-chat',
    api_key=os.getenv('DEEPSEEK_API_KEY')
)


# Define a template for answering questions
template = '''
Answer the following questions as best you can.
Questions: {q}
'''

# Create a PromptTemplate object from the template
prompt_template = PromptTemplate.from_template(template)

# Pull the react prompt from the hub
prompt = hub.pull('hwchase17/react')

# displaying information about the react prompt
# print(type(prompt))
# print(prompt.input_variables)
# print(prompt.template)


# Create tools for the agent

# 1. Python REPL Tool (for executing Python code)
python_repl = PythonREPLTool()
python_repl_tool = Tool(
    name='Python REPL',
    func=python_repl.run,
    description='Useful when you need to use Python to answer a question. You should input Python code.'
)

# 2. Wikipedia Tool (for searching Wikipedia)
api_wrapper = WikipediaAPIWrapper()
wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)
wikipedia_tool = Tool(
    name='Wikipedia',
    func=wikipedia.run,
    description='Useful for when you need to look up a topic, country, or person on Wikipedia.'
)

# 3. DuckDuckGo Search Tool (for general web searches)
search = DuckDuckGoSearchRun()
duckduckgo_tool = Tool(
    name='DuckDuckGo Search',
    func=search.run,
    description='Useful for when you need to perform an internet search to find information that another tool can\'t provide.'
)

# Combine the tools into a list
tools = [python_repl_tool, wikipedia_tool, duckduckgo_tool]

# Create a react agent with the ChatOpenAI model, tools, and prompt
agent = create_react_agent(llm, tools, prompt)

# Initialize the AgentExecutor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10
)

# question = 'Generate the first 20 numbers in the Fibonacci series.'
# question = 'Who is the current prime minister of the UK?'
question = 'Hi'
output = agent_executor.invoke({
    'input': prompt_template.format(q=question)
})