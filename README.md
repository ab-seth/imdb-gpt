# imdb-gpt
A Python GPT-based Chatbot for querying data from IMDB  dataset

## Installation

Run:
```bash
pip install -r requirements.txt 
```
**Note:** This will install required libraries listed the requirements.txt file with their respective versions.
in case you experience any version issues, especially for openai, run:
```bash
pip install --upgrade openai
```

Next, set your OpenAI API Key as an environment variable:
```bash
export OPENAI_API_KEY="YOUR_KEY"
```


## Downloading Data
1. Download the [IMDB dataset](https://datasets.imdbws.com/)
1. Extract all files
1. Place all TSV files under a directory named `/imdb-data` in this repo's cloned directory


## Build local DB
Run:
```bash
python create_local_db.py
```
This will generate a file called `imdb.db`
**Note:** This process might take 10-15 minutes to complete.


## Run bot
Run:
```bash
streamlit run imdb-gpt.py
```


