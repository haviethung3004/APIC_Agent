# **APIC Agent**

The **APIC Agent** is an intelligent assistant designed to interact with Cisco's Application Centric Infrastructure (ACI) tool. It leverages LangChain, Fireworks AI, and custom tools to query, process, and manage ACI configurations dynamically. The agent supports tasks such as fetching tenant information, checking bridge domains, and executing Python code for data processing.

---

## **Table of Contents**
1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [License](#license)

---

## **Features**
- **Dynamic Tool Integration**: Includes tools like `get_apic`, `get_uri`, and `python_repl` for interacting with the APIC API and executing Python code.
- **Fuzzy Matching**: Automatically matches user input to predefined URIs in `urls.json`.
- **React Agent**: Uses reasoning and action-based decision-making to handle complex queries.
- **Customizable Prompts**: Provides a flexible prompt template for guiding agent behavior.
- **Backup Support**: Allows saving fetched data to local files (e.g., `backup.json`).

---

## **Project Structure**
The project is organized into the following directories and files:
├── apic_agent
│ ├── agent_tool.py # Custom tools for the agent
│ ├── apic_client.py # APIC API client implementation
│ ├── init .py # Package initialization
│ ├── urls.json # Predefined URIs for fuzzy matching
├── main.py # Entry point for the application
├── README.md # This file
└── requirements.txt # Python dependencies

## **Installation**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/haviethung3004/APIC_Agent.git
   cd APIC-Agent

2. **Install Dependencies**:
   ```bash
    pip install -r requirements.txt

3. **Configure Environment Variables**:
   ```bash
   vim .env

   APIC_BASE_URL = YOUR_APIC_BASE_URL
   APIC_USERNAME = YOUR_APIC_USERNAME
   APIC_PASSWORD = YOUR_APIC_PASSWORD
   OPENAI_API_KEY = YOUR_OPENAI_API_KEY

