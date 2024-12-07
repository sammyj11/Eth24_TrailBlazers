import socket
import threading
import openai
import time
from typing import List, Dict
from openai import RateLimitError, APIError


# Initialize OpenAI API Key
openai_api_key="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"

openai.api_key = openai_api_key

# Define the Specialized Agent Class (Agent for different sectors)
class SpecializedAgent:
    def __init__(self, domain: str, peer_id: str):
        self.domain = domain
        self.peer_id = peer_id

    def query_gpt(self, news: str) -> str:
        """Query GPT for context generation with error handling for rate limits"""
        prompt = f"You are an expert in {self.domain}. Based on the following news, provide context and analysis that could influence stock trading decisions.\n\nNews: {news}\n\nContext:"

        max_retries = 2
        retry_delay = 2  # Start with a 2-second delay for retries
        attempt = 0
        
        while attempt < max_retries:
            try:
                # Use the new API format with chat_completions.create
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # or gpt-4, based on what you want to use
                    messages=[
                        {"role": "system", "content": f"You are a {self.domain} expert."},
                        {"role": "user", "content": prompt}
                    ]
                )

                return response['choices'][0]['message']['content'].strip()
            
            except RateLimitError as e:
                print(f"Rate limit exceeded. Retrying... Attempt {attempt + 1}/{max_retries}")
                attempt += 1
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff: Double the wait time after each retry
            except APIError as e:
                print(f"API error occurred: {e}")
                break  # In case of other API errors, stop retrying
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        return "Error: Unable to process the request after several retries."


# Define the Master LLM Class
class MasterLLM:
    def __init__(self, specialized_agents: Dict[str, SpecializedAgent]):
        self.specialized_agents = specialized_agents

    def determine_relevant_domains(self, news: str) -> List[str]:
        """Determine the relevant sectors based on news content"""
        relevant_domains = []
        if "oil" in news or "gas" in news:
            relevant_domains.append('oil_and_gas')
        if "pharmaceutical" in news:
            relevant_domains.append('pharmaceuticals')
        if "automotive" in news:
            relevant_domains.append('automotive')
        if "steel" in news:
            relevant_domains.append('steel_industry')
        return relevant_domains

    def process_user_input(self, news: str) -> str:
        """Process user input, get relevant context from agents, and generate a summary"""
        relevant_domains = self.determine_relevant_domains(news)
        context_from_agents = []

        print(f"Master LLM: Analyzing news - '{news}'")

        for domain in relevant_domains:  # Select up to two relevant domains
            agent = self.specialized_agents[domain]
            print(f"Master LLM: Consulting the '{domain}' agent for context...")
            context = agent.query_gpt(news)
            context_from_agents.append(context)

        combined_context = " ".join(context_from_agents)
        summary = f"Summary for Trading Bot: {combined_context[:500]}"

        return summary


# Define the Trading Bot Class
class TradingBot:
    def __init__(self, initial_budget: float = 100000.0):
        self.balance = initial_budget
        self.trade_history = []

    def execute_trade(self, analysis: str):
        """Simulate executing a trade based on the analysis"""
        print(f"\nTrading Bot: Analyzing the summary: {analysis}")
        
        if "increase" in analysis.lower():
            trade_action = "BUY"
            trade_amount = 5000  # Simulate a fixed trade amount for simplicity
            self.balance -= trade_amount
        elif "decrease" in analysis.lower():
            trade_action = "SELL"
            trade_amount = 3000  # Simulate a fixed trade amount for simplicity
            self.balance += trade_amount
        else:
            trade_action = "HOLD"
            trade_amount = 0

        self.trade_history.append((trade_action, trade_amount))
        self.print_trade_summary(trade_action, trade_amount)

    def print_trade_summary(self, action, amount):
        print(f"Trading Bot: Action - {action}, Amount - ${amount:.2f}")
        print(f"Trading Bot: Remaining Balance - ${self.balance:.2f}\n")


# Socket Server for Master LLM to communicate with agents
def start_master_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)
    print("Master Server listening on port 12345...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Master Server: Connected to {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    """Handle incoming messages from agents"""
    data = client_socket.recv(1024).decode()
    print(f"Master Server received data: {data}")
    response = "Master LLM: Acknowledged your message"
    client_socket.send(response.encode())
    client_socket.close()


# Socket Client to simulate the communication between Master LLM and the agents
def master_communication(master_socket, master_llm, trading_bot, news_items):
    """Simulate sending a query to the master LLM for each news item and executing trades"""
    for news_item in news_items:
        print(f"Master LLM: Processing news - '{news_item}'")
        
        # Process the user input through Master LLM
        analysis = master_llm.process_user_input(news_item)
        
        # Send the generated summary to the trading bot for execution
        print(f"Master LLM: Generated Summary: {analysis}")

        # Simulate sending this to the trading bot for execution
        trading_bot.execute_trade(analysis)
        time.sleep(1)  # Simulate periodic trade execution

def main():
    # Initialize specialized agents (representing different sectors)
    peer_ids = {
        'oil_and_gas': 'peer-oil-and-gas-id',
        'pharmaceuticals': 'peer-pharma-id',
        'automotive': 'peer-auto-id',
        'steel_industry': 'peer-steel-id',
    }

    specialized_agents = {domain: SpecializedAgent(domain, peer_id) for domain, peer_id in peer_ids.items()}

    # Initialize the Master LLM
    master_llm = MasterLLM(specialized_agents)

    # Initialize the trading bot
    trading_bot = TradingBot(initial_budget=100000.0)
    
    # Start the server that listens for incoming agent messages
    threading.Thread(target=start_master_server, daemon=True).start()

    # Simulate communication from the client side (Master LLM)
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.connect(('localhost', 12345))  # Connect to the Master Server
    print("Client connected to Master Server")

    # List of news items for multiple interactions
    news_items = [
        "The oil prices have surged due to new geopolitical tensions, and the pharmaceutical market is facing regulatory changes.",
        "automotive stocks are experiencing volatility due to a global chip shortage affecting production rates.",
        "steel production is increasing globally as demand for infrastructure projects rises, especially in emerging markets.",
        "The pharmaceutical industry is pushing for more aggressive regulation in the US following a major drug safety recall."
    ]

    # Start the communication with multiple news items
    master_communication(master_socket, master_llm, trading_bot, news_items)

if __name__ == "__main__":
    main()
