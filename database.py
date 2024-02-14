import sqlite3

DB_FILENAME = 'imdb.db'
QUERY_RESULT_MAX_LENGTH = 2000


def connect_to_database():
    """Connects to the IMDB database and returns a cursor."""
    conn = sqlite3.connect(DB_FILENAME)
    return conn.cursor()

def execute_query(query: str) -> str:
    """Executes a SQL query and returns the output in markdown table format."""
    try:
        cursor = connect_to_database()
        cursor.execute(query)
        header = [description[0] for description in cursor.description]
        data = cursor.fetchall()
    except Exception as e:
        return f"Error while running query: {e}"

    if not data:
        return ""

    # Formatting the header
    header_line = '| ' + ' | '.join(header) + ' |'
    separator_line = '|---' * len(header) + '|'

    # Formatting the data
    data_lines = []
    for row in data:
        row_line = '| ' + ' | '.join(str(item) for item in row) + ' |'
        data_lines.append(row_line)

    # Joining all parts into a single string
    markdown_table = '\n'.join([header_line, separator_line] + data_lines)

    # Return an error if the result is too large, as there's a limit on the number of tokens.
    if len(markdown_table) <= QUERY_RESULT_MAX_LENGTH:
        return markdown_table
    else:
        return "Error: query result is too large."

