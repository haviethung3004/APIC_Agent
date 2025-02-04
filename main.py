from apic_agent.apic_client import APICClient
import apic_agent.langchain_agent

def main():
    print("Welcome to the Cisco ACI Agent!")
    
    try:
        # Initialize the APIC client with credentials (you can modify this to accept user input if needed)
        apic_client = APICClient()
                
        while True:
            # Prompt the user for a question
            question = input("\nEnter your question (or type 'exit' to quit): ").strip()
            
            # Exit condition
            if question.lower() in ['exit', 'quit']:
                print("Exiting the Cisco ACI Agent. Goodbye!")
                break
            
            # Get the response from the bot
            response = bot.get_response(question)
            
            # Print the agent's response
            print(f"\nAgent Response: {response}")
    
    except Exception as e:
        # Handle any unexpected errors gracefully
        print(f"An error occurred: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()