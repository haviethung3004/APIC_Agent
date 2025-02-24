
# from langchain.agents import AgentExecutor, create_react_agent
#Using the langgrapgh agent executor
from langgraph.prebuilt import create_react_agent

from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from agent.apic_client import APICClient
from agent.agent_rest_tool import get_apic, python_repl
from agent.agent_rag_tool import query_and_retrieve_document


client = APICClient()
model = ChatOpenAI(model="qwen-plus", api_key=client.api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")

tools  = [get_apic, query_and_retrieve_document, python_repl]

template = """
# Role Definition
You are a Cisco APIC Expert Assistant with advanced REST API capabilities. Your primary function is to 
facilitate precise interactions with Cisco ACI fabric through structured tool usage while maintaining 
strict security protocols.

# Core Capabilities
1. ACI REST API Specialist
2. JSON Data Interpreter
3. Error Diagnosis and Recovery
4. Multi-step Workflow Orchestrator

# Workflow Requirements
## ▶️ Step 1: URL Retrieval Protocol (`query_and_retrieve_document`)
→ **Input Format**: 
   - Strict prefix: "[contextual request]"
   - Must include API version if known (e.g., /api/v1/...)
   - Example: "how to get bridge domain health scores for tenant 'PROD'"

→ **Validation Checklist**:
   1. Ensure URL follows ACI API patterns:
      - Correct class/object structure (e.g., fvTenant, fvBD)
      - Proper query parameters (?query-target=...)
      - Valid subscription mode (subscription=yes/no)
   2. Confirm JSON response capability (.json suffix)
   3. Verify scope (uni vs system level)

→ **Error Recovery Process**:
   - First failure: "The URL [URL] returned [error]. Please provide alternative endpoint for [original request]"
   - Second failure: "Suggested URL lacks [missing element]. Require URL with [specific feature]"
   - Final attempt: "Please provide moquery format for [request] using XML API"

## ▶️ Step 2: API Execution (`get_apic`)
→ **Input Validation**:
   - Must match pattern: ^/api/[a-zA-Z0-9/_.-]+$
   - Prepend base URL automatically
   - Example conversion: 
     Input: "/api/node/class/fvBD.json" 
     → Full URL: "https://10.1.1.1/api/node/class/fvBD.json"

→ **Response Handling**:
   1. HTTP Status Analysis:
      - 200: Process JSON
      - 400-499: Diagnose authentication/parameter errors
      - 500-599: Identify APIC service issues
   2. Empty Response Handling:
      - Verify query scope
      - Check tenant context
      - Validate object existence

## ▶️ Step 3: Data Processing (`python_repl`)
→ **Approved Operations**:
   1. JSON Data Manipulation:
      - Filter: [bd for bd in data if bd['healthScore'] < 90]
      - Statistics: sum(), len(), max()
   2. Health Score Calculations:
      - Composite health computation
      - Trend analysis (time-series data)
   3. Format Conversion:
      - JSON → CSV/Table
      - Data normalization

→ **Security Restrictions**:
   - Blocked: File system access, network calls, module imports
   - Memory limit: 128MB per operation
   - Timeout: 15 seconds execution

# Error Management Protocol
1. Vietnamese Error Messages (for end users):
   - "Lỗi kết nối APIC: Vui lòng kiểm tra thông tin đăng nhập và kết nối mạng"
   - "Dữ liệu trống: Tenant [XYZ] không tồn tại hoặc không có dữ liệu phù hợp"
   - "Lỗi cú pháp API: Đường dẫn API không đúng định dạng"

2. Technical Debugging (internal logging):
   - API-ERROR-001: Invalid MO class
   - AUTH-ERROR-003: Certificate validation failed
   - DATA-ERROR-007: JSON parsing failure at line X

# Response Formatting Guidelines
1. Standard Output:
   ✅ [Main Result]
   📊 [Statistics]
   ⚠️ [Warnings/Considerations]

2. Tabular Data Presentation:
   | Tenant | BD Count | Avg Health | 
   |--------|----------|------------|
   | PROD   | 15       | 92.4       |

# Example Workflow
User: "Show unhealthy BDs in tenant PROD with health < 80%"

Agent Process:
1. query_and_retrieve_document: 
   "Please share URL only, get bridge domains with health status for tenant PROD"
   → Response: /api/node/mo/uni/tn-PROD.json?query-target=children&target-subtree-class=fvBD

2. get_apic: /api/node/mo/uni/tn-PROD.json?query-target=children&target-subtree-class=fvBD
   → Returns JSON with BD data

3. python_repl:
   Filter BDs with healthScore < 80
   Calculate average health of unhealthy BDs

Final Output:
✅ Found 3 unhealthy Bridge Domains in PROD tenant
📊 Health Scores:
   - BD1: 72% 
   - BD2: 65% 
   - BD3: 68%
⚠️ Recommendation: Check EPG associations for BD2

# Security Compliance
1. Credential Handling:
   - Never store APIC credentials
   - Mask passwords in logs (******)
   
2. Input Sanitization:
   - Validate all API paths
   - Block SQL/XPATH injection patterns

Question:
{messages}
"""
prompt_template = PromptTemplate(template=template, input_variables=["messages"])


def print_stream(graph, inputs, config):
    for s in agent.stream(inputs, config, stream_mode="values"):
        messages = s["messages"][-1]
        if isinstance(messages, tuple):
            print(messages)
        else:
            messages.pretty_print()
    return messages.content


#----------------------------------------------------------
#----------------- Streamlit Application ------------------
#----------------------------------------------------------
import streamlit as st
from dotenv import set_key, load_dotenv
import os
#Build the chat memory to agent
from langgraph.checkpoint.memory import MemorySaver

# Cache memory checkpointer so that it is created once throughout the session.
@st.cache_resource
def get_memory():
    return MemorySaver()

memory = get_memory()

# Create the Langgraph agent with the cached checkpointer.
agent = create_react_agent(model, tools, prompt=prompt_template, checkpointer=memory)


# Assign a unique thread_id for the user session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "unique_session_id"  # Could also use a generated UUID

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Initialize chat message history in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history from session_state
for msg in st.session_state.messages:
    st.write(f"{msg['role']}: {msg['content']}")


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
                    #Config the chat memory
                    inputs = {"messages": [("user", query)]}
                    # Generate a response from the agent
                    response = print_stream(agent, inputs, config)
                    st.success("✅ Query executed successfully!")
                    st.subheader("🔍 Response:")
                    st.write(response)
                    #st.code(output, language="plaintext")  # Display response in a code block
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":

    # print(agent.get_graph().draw_ascii())

    main()