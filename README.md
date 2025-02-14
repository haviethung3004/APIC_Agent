# APIC Agent

This project integrates with **Cisco ACI (Application Centric Infrastructure)** using LangChain and four different API keys for various functionalities. The goal is to interact with Cisco ACI for better automation, configuration, and management.

## API Keys Required

To run this project, you will need to configure the following API keys:

1. **[UnstructuredLoader](https://unstructured.io/)**: Used for splitting and chunking unstructured data.
2. **[Gemini](https://www.pinecone.io/)**: Provides embedding capabilities to transform data into vectors.
3. **[Pinecone](https://www.pinecone.io/)**: Used for storing and querying vectors in a vector database.
4. **[ChatOpenAI](https://openai.com/index/openai-api/)**: Powers the chatbot for natural language understanding and interaction.

Make sure to set up the necessary API keys in your environment for the project to function correctly.

## Cisco ACI Sandbox Setup

If you don't have a physical Cisco ACI environment, you can use **Cisco's Sandbox** to set up and test your ACI integration. Cisco provides an online lab environment for hands-on experience with their products, including ACI.

To set up a **Cisco ACI** Sandbox, follow these steps:

1. **Sign up for a Cisco DevNet account**:
   - Visit [Cisco DevNet](https://developer.cisco.com/) and sign up for a free account if you haven't already.

2. **Access the Cisco ACI Sandbox**:
   - Go to [Cisco DevNet Sandbox](https://devnetsandbox.cisco.com/) and search for the **ACI** sandbox.
   - Select the **ACI Sandbox** and click **Reserve** to book a session.

3. **Obtain the ACI Access Details**:
   - After reserving the sandbox, you'll be provided with the necessary **ACI IP address**, **username**, and **password** for accessing Cisco ACI.

## Project Structure

```
.
├── README.md                 # Project documentation
├── agent                     # Contains agent-related scripts
│   ├── __init__.py
│   ├── agent_rag_tool.py     # RAG tool for agent
│   ├── agent_rest_tool.py    # REST API interaction tool
│   ├── apic_client.py        # Cisco ACI client
│   └── content
│       └── docs
│           ├── cisco-apic-rest-api-configuration-guide-42x-and-later.pdf
│           └── example_urls.txt
├── main.py                   # Main entry point for the application
└── requirements.txt          # Python dependencies
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/haviethung3004/APIC_Agent.git
   cd APIC_Agent
   ```

2. **Install dependencies** using Pipenv:

   ```bash
   pipenv install
   ```

3. **Set up environment variables**:
   Ensure you have the following API keys set as environment variables:

   - `UNSTRUCTURED_API_KEY`
   - `GEMINI_API_KEY`
   - `PINECONE_API_KEY`
   - `OPENAI_API_KEY`
   - `APIC_BASE_URL`
   - `APIC_USERNAME`
   - `APIC_PASSWORD`

   Create a `.env` file and save the these API_KEY 

4. **Configure Cisco ACI connection**:
   If you're using the Cisco ACI Sandbox, make sure you have the API endpoint and credentials from the sandbox setup. Update the `apic_client.py` file to include your connection details.

5. **Set up vector db**:
   Set up vector db for agent_rag_tool(Refer README file in agent)

6. **Run the project**:

   Once everything is set up, you can run the project using:

   ```bash
   streamlit run main.py
   ```

## Usage

The `main.py` file serves as the entry point for the application. It interacts with Cisco ACI using the provided API keys and LangChain to automate tasks.

### Example

```bash
python main.py --action <action_name> --parameters <parameters>
```

Replace `<action_name>` and `<parameters>` with the desired actions and parameters for the task you wish to perform.

## Contributing

Feel free to fork the repository and submit pull requests. If you encounter any issues or have suggestions for improvements, please open an issue.

### Code of Conduct

By contributing to this project, you agree to adhere to our code of conduct.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

Now, the README reflects the specific roles of the APIs in your project. Let me know if there's anything else you'd like to add or adjust!