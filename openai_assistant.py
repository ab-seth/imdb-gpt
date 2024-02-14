import openai
from textwrap import dedent
from database import execute_query
import json


QUERY_RESULT_MAX_LENGTH = 2000

client = openai.OpenAI()

def get_schemas() -> str:
    """
    Return table schemas in TOML formatting:
    
    [table_name]
    column_name (type) = description
    """
    with open("tables.toml", "r") as f:
        return f.read()

def get_system_prompt() -> str:
    """Returns the system prompt with table schemas."""
    system_prompt = {
    "role": "system", 
    "content": dedent(f"""You are an expert and useful IMDB assistant. You only use the data provided to you to reply on questions and and do not attempt any other questions which are outside the data provided.
               The tables you can use and their descriptions are provided below in TOML format in the following way:
                
                [table_name]
                column_name (type) = description
                
                Tables:
                ```
                {get_schemas()}
                ```
                
               IMPORTANT: You can only rely on the data from these tables.""")
}
    return system_prompt

def get_instructions() -> str:
    """Returns the instructions for the assistant."""
    instructions = dedent("""IMPORTANT:
                      * When creating SQL queries, use SQLite syntax. Arrays are stored as TEXT with commas separating values
                      * Your response must be human-readable and understandable to the average user. 
                      * Identifiers and IDs are internal, and should not be presented to the user.
                      """)
    return instructions

def get_tools() -> list:
    """Returns the list of tools for the assistant."""
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
    return tools

def ask_question(question: str, model: str, verbose: bool) -> str:
    """
    Asks GPT the user's question

    @param question: the user's question
    @para model: the OpenAI model to use
    """
    messages = [get_system_prompt(), {"role": "user", "content": f"{question}\n{get_instructions()}"}]

    final_message = False
    while not final_message:
        if verbose:
            print(f" -> Querying {model}")
        completion = client.chat.completions.create(model=model, temperature=0., messages=messages, tools=get_tools())
        assistant_message = completion.choices[0].message
        messages.append(assistant_message)
        
        if assistant_message.tool_calls:
            for i in range(len(assistant_message.tool_calls)):
                query = json.loads(assistant_message.tool_calls[i].function.arguments)['query']
                if verbose:
                    print(f" -> Running SQL query: {query}")
                query_result = execute_query(query)
                messages.append({
                    "tool_call_id": assistant_message.tool_calls[i].id,
                    "role": "tool",
                    "name": "query_result_as_markdown_table",
                    "content": query_result
                })
        else:
            final_message = True
            
    return(messages[-1].content)

