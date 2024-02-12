import json
import sqlite3
import argparse
from textwrap import dedent
from openai import OpenAI

# Constants
QUERY_RESULT_MAX_LENGTH = 2000
DB_PATH = 'imdb.db'
TABLES_TOML_PATH = "tables.toml"

# Database Context Manager
class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# OpenAI Client
class OpenAIChatClient:
    def __init__(self):
        self.client = OpenAI()

    def ask_question(self, question: str, model: str, verbose: bool) -> str:
        system_prompt = self._generate_system_prompt()
        messages = [system_prompt, {"role": "user", "content": f"{question}\n{instructions}"}]
        
        final_message = False
        while not final_message:
            if verbose:
                print(f" -> Querying {model}")
            completion = self.client.chat.completions.create(model=model, temperature=0., messages=messages, tools=tools)
            assistant_message = completion.choices[0].message
            messages.append(assistant_message)
            
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    query = json.loads(tool_call.function.arguments)['query']
                    if verbose:
                        print(f" -> Running SQL query: {query}")
                    query_result = query_result_as_markdown_table(query)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "query_result_as_markdown_table",
                        "content": query_result
                    })
            else:
                final_message = True
                
        return messages[-1].content

    def _generate_system_prompt(self) -> dict:
        return {
            "role": "system",
            "content": dedent(f"""You are an expert and useful IMDB assistant. You only use the data provided to you to reply on questions.
                            The tables you can use and their descriptions are provided below in TOML format in the following way:

                            [table_name]
                            column_name (type) = description

                            Tables:
                            ```
                            {get_schemas()}
                            ```

                            IMPORTANT: You can only rely on the data from these tables.""")
        }

def get_schemas() -> str:
    with open(TABLES_TOML_PATH, "r") as f:
        return f.read()

def query_result_as_markdown_table(query: str) -> str:
    try:
        with DatabaseConnection(DB_PATH) as cursor:
            cursor.execute(query)
            header = [description[0] for description in cursor.description]
            data = cursor.fetchall()
    except Exception as e:
        return f"Error while running query: {e}"
    
    if not data:
        return ""

    markdown_table = _format_as_markdown_table(header, data)
    return "Error: query result is too large." if len(markdown_table) > QUERY_RESULT_MAX_LENGTH else markdown_table

def _format_as_markdown_table(header: list, data: list) -> str:
    header_line = '| ' + ' | '.join(header) + ' |'
    separator_line = '|---' * len(header) + '|'
    data_lines = ['| ' + ' | '.join(str(item) for item in row) + ' |' for row in data]
    return '\n'.join([header_line, separator_line] + data_lines)

instructions = dedent("""IMPORTANT:
                        * When creating SQL queries, use SQLite syntax. Arrays are stored as TEXT with commas separating values
                        * Your response must be human-readable and understandable to the average user. 
                        * Identifiers and IDs are internal, and should not be presented to the user.
                        """)

tools = [
    {
        "type": "function",
        "function": {
            "name": "query_result_as_markdown_table",
            "description": "This function takes a SQL query, runs it in the database and returns the output table in markdown format",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "the SQL query to run. Its output will be returned as a markdown table"
                    }
                },
                "required": ["query"],
            }
        }
    }
]

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-m', '--model', default='gpt-4', help='Name of OpenAI chat model to use', dest='model')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode', dest='verbose')
    args = arg_parser.parse_args()

    chat_client = OpenAIChatClient()

    print(f"[Running using {args.model}]")
    print("\nWelcome! Ask as many IMDB-related questions as you would like. To exit, press Ctrl+C.")
    if args.verbose:
        print("Verbose mode on.")
    print("\n")

    while True:
        question = input("What would you like to know? ")
        response = chat_client.ask_question(question, model=args.model, verbose=args.verbose)
        print(response + '\n')
