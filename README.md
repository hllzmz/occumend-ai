<img width="1017" height="450" alt="banner-oai" src="https://github.com/user-attachments/assets/bf1c202d-7538-40ee-8fe1-1abdef488d72" />

# OccumendAI
An AI-based career recommendation engine as a Flask web application.

[Go to site](https://www.occumendai.app)
## How it works?
OccumendAI is a career recommender.  Using various occupational information and characteristics from the ONET® 30.0 Database, it provides career advice. 

[To have a detailed look at the development process ](https://medium.com/@halil.uzmez/occumendai-building-an-ai-powered-career-recommendation-engine-from-scratch-f62f51f16f17)

### Stage 1: Survey and Recommendations
First, the user completes the RIASEC (Holland Code Test) scale, and a user profile is generated. Occupational interests provided by ONET are clustered using KMeans to determine real-world occupational interest clusters (8 in total). The user profile is compared to the O*NET occupational profile using cosine similarity, and a similarity score is calculated. Occupational recommendations are made based on the similarity score and presented to the user along with the occupational interest clusters to which the occupations belong.

### Stage 2: RAG and Chat
The occupational information provided by ONET (e.g., Abilities, Skills, Tasks, etc.) has been exported to a JSON file in the format “doc_id, title, content”. The JSON file, referred to as the “ONET knowledge base”, has been converted into embeddings using sentence transformers in chunks. The user profile and knowledge base created with the scale are fed into the LLM to create a RAG implementation that enables the user to chat about recommendations and occupational information.

## Run Locally
1. Clone repo
```bash
git clone https://github.com/hllzmz/occumend-ai.git
```
2. Change to project directory
```bash
cd occumend-ai
```
3. Create a virtual environment
```bash
python -m venv .venv
```
4. Activate the virtual environment
```bash
source .venv/bin/activate (MacOS and Linux)

\venv\Scripts\Activate.ps1 (Windows Powershell)
\venv\Scripts\activate.bat (Windows CMD)
```
5. Install requirements
```bash
pip install -r requirements.txt
```
6. Set .env variables (Get your api key from [openrouter.ai](https://openrouter.ai/))

(The chat function has been implemented using the OpenAI SDK. Any OpenAI chat-compatible provider can be used. Just edit the code in config.py and services.py.)
```bash
OPEN_ROUTER_API_KEY=sk... (default)
OPENAI_API_KEY=sk... (optional)
```
7. Start the app with Flask
```bash
python run.py
```
or 

Start the app with WSGI server
```bash
gunicorn --bind 0.0.0.0:5000  run:app
```
The LLM to be used for chat can be run locally with tools such as Ollama or LM Studio (config.py, services.py) after making the necessary changes.


## Build and Run Locally with Docker Compose

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key

3. Build and run with Docker Compose:
   ```bash
   docker compose up --build -d
   ```

4. Check the logs:
   ```bash
   docker compose logs -f
   ```
5. Stop the app
   ```bash
   docker compose down --remove-orphans
   ```

### Pull From Docker Registry and Run
1. Pull the Docker image:
   ```bash
   docker pull haliluzmez/occumendai:v1
   ```
2. Run with Docker
   ```bash
   docker run -p 5000:5000 --env-file .env haliluzmez/occumendai:v1
   ```

## Data Source

This project uses data from the **O*NET® Database**, provided by the U.S. Department of Labor, Employment and Training Administration.

- Database: [O*NET Database](https://www.onetcenter.org/database.html)  
- License: [O*NET License Agreement](https://www.onetcenter.org/license_db.html)  
- Note: This repository does **not contain the original O*NET database files**. Only processed or derived data are included.
