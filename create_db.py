import csv
import toml
import sqlite3

# Constants
CSV_FIELD_SIZE_LIMIT = 1310720 * 10 # some tables were larger than allowable size, increase to sys max if possible
DB_FILENAME = 'imdb.db'
DATA_FOLDER = 'imdb-data'
TABLES_FILE = "tables.toml"
NULL_REPRESENTATION = '\\N'

# Increase the maximum size for CSV field
csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)

def flatten_list(nested_list):
    """Flatten a nested list into a flat list."""
    flattened = []

    def flatten(sublist):
        for item in sublist:
            if isinstance(item, list):
                flatten(item)
            else:
                flattened.append(item)

    flatten(nested_list)
    return flattened

def create_table(cursor, table_name, field_definitions):
    """Create a SQL table with the given name and field definitions."""
    column_definitions = []

    for field, data_type in field_definitions.items():
        field_name = field.split(' ')[0]
        field_type = data_type.lower() if data_type in ['int', 'float'] else 'text'
        column_definitions.append(f"{field_name} {field_type}")

    columns_sql = ", ".join(column_definitions)
    sql = f"CREATE TABLE {table_name} ({columns_sql})"
    cursor.execute(sql)

def load_data_into_table(cursor, table_name, file_path, num_columns):
    """Load data into the given table from the specified TSV file."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        headers = next(tsv_reader)  # Skip the header row

        for row in tsv_reader:
            if len(row) != num_columns:
                row = flatten_list([v.split('\t') for v in row])
            row = [None if v == NULL_REPRESENTATION else v for v in row]
            placeholders = ', '.join(['?'] * num_columns)
            cursor.execute(f'INSERT INTO {table_name} VALUES ({placeholders})', row)

def main():
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    tables = toml.load(TABLES_FILE)
    for table_name, fields in tables.items():
        print(f"Creating table: {table_name}...")
        create_table(cursor, table_name, fields)

    for table_name in tables:
        file_path = f'{DATA_FOLDER}/{table_name.replace("_", ".")}.tsv'
        num_columns = len(tables[table_name])
        print(f"Loading data into {table_name}...")
        load_data_into_table(cursor, table_name, file_path, num_columns)

    conn.commit()
    conn.close()
    print('Done.')

if __name__ == "__main__":
    main()
