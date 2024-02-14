import argparse
from database import execute_query
from openai_assistant import (
    ask_question,
    get_instructions,
    get_schemas,
    get_system_prompt,
    get_tools,
)
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-m', '--model', default='gpt-4', help='Name of OpenAI chat model to use', dest='model')
    arg_parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Enable verbose mode', dest='verbose')
    args = arg_parser.parse_args()

    print(f"[Running using {args.model}]")
    print("\nWelcome! Ask as many IMDB-related questions as you would like. To exit, press Ctrl+C.")
    if args.verbose:
        print("Verbose mode on.")
    print("\n")

    while True:
        question = input("What would you like to know? ")
        response = ask_question(question, model=args.model, verbose=args.verbose)
        print(response + '\n')