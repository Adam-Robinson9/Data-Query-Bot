# AI Data Query Bot

An AI powered chatbot that answers natural language questions about an uploaded database, providing an answer and a generated plot if required.
Built with Python, Flask, HTML/CSS and deployed with Azure App Service.

Try it live: dataquerybot-hph4dhb8edecg2hg.francecentral-01.azurewebsites.net

(Note: hosted on Azure’s free tier — the first request may take up to several minutes to load.)

## Features
- Upload any CSV file using a simple web interface.
- Ask natural language questions about the dataset.
- Automatically generates Python code to answer queries, using OpenAI API.
- Returns the answer/plot and the code generated for the question.

## Tech Stack
* Python (Flask)
* HTML, CSS
* Pandas, Numpy, Matplotlib
* OpenAI API
* Azure App Service

## Local setup

### 1. Clone the repository
git clone https://github.com/Adam-Robinson9/Data-Query-Bot.git

cd Data-Query-Bot

### 2. Create virtual environment
python -m venv venv

source venv/bin/activate   # Mac/Linux

venv\Scripts\activate      # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment
Create .env file: 

OPENAI_API_KEY=*Your OpenAI API key*

### 5. Run locally
python app.py

## Author
Adam Robinson. Computer Science and Maths student, University of Leeds.
