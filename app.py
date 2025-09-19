# Import libraries
from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import io, contextlib,os
from openai import OpenAI
import matplotlib
matplotlib.use("Agg")  # Stop plots displaying to GUI
import matplotlib.pyplot as plt
import base64
import builtins
from dotenv import load_dotenv
load_dotenv() # Load .env file for OpenAI API key

# Initialize Flask
app = Flask(__name__)

# Create data frame to store the csv data in
df = pd.DataFrame()

# Initialize OpenAI API connection
key = os.getenv("OPENAI_API_KEY")
if not key:
    raise RuntimeError("OPENAI_API_KEY not loaded from .env")
client = OpenAI(api_key=key.strip())

# Route to upload a CSV file
@app.route("/upload", methods=["POST"])
def upload_csv():
    global df
    # Get file from HTTP request
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Try to read data from CSV file into data frame
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV: {str(e)}"}), 400

    # Return success message and column names if process is successful
    return jsonify({
        "message": "File uploaded successfully",
        "columns": df.columns.tolist()
    })

# Route to ask a question about the data
@app.route("/query", methods=["POST"])
def query_data():
    global df
    # Make sure a dataset has been uploaded first
    if df.empty:
        return jsonify({"error": "No dataset uploaded yet."}), 400

    # Extract user's question from HTTP request
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Create a summary of the dataset (small preview + schema)
    preview = df.head(5)
    schema = df.dtypes

    # Build prompt for OpenAI
    input_prompt = f"""
    You are a Python data assistant. The user has uploaded a dataset, described as follows:

    Schema: {schema}
    First 5 rows: {preview}

    User's question: {question}

    Write Python code using Pandas that:
    1. Analyzes the dataframe: `df`
    2. Prints the answer (with print statements) to only the question asked by the user, and nothing else.

    Return ONLY valid Python code. Do not include comments, explanations, markdown, or text outside the code.
    Important: Do not include import statements. The following libraries are already available: pandas as pd, matplotlib.pyplot as plt, and numpy as np.
    """

    try:
        # Send prompt to API
        response = client.responses.create(
            model="gpt-5-nano",
            input=input_prompt,
            store=True,
        )

        # Extract code from API response
        code = response.output_text

        try:
            # Run generated code
            answer = execute_code(code)
        except Exception as e:
            return jsonify({"error": f"Execution failed: {str(e)}"}), 400
            
        # Collect any generated plots as base64 images
        images = []
        figures = [plt.figure(n) for n in plt.get_fignums()]
        for figure in figures:
            buffer = io.BytesIO()
            figure.savefig(buffer, format="png")
            buffer.seek(0)
            images.append(base64.b64encode(buffer.read()).decode("utf-8"))
            plt.close(figure) 

    except Exception as e:
        return jsonify({"error": f"OpenAI API request failed: {str(e)}"}), 500

    # Return results: code, answer, images & user's question
    return jsonify({
        "code": code,
        "answer": answer,
        "images": images,
        "question": question
    })

# Safely execute the generated code
def execute_code(code: str):
    # Start with all of the python builtins
    allowed_builtins = dict(vars(builtins))
    # Remove dangerous builtins
    banned = ["open", "exec", "eval", "__import__", "compile", "input"]
    for b in banned:
        if b in allowed_builtins:
            del allowed_builtins[b]

    # Create buffer to capture code output
    answer_buffer = io.StringIO()
    with contextlib.redirect_stdout(answer_buffer):
        exec(
            code, 
            {"__builtins__": allowed_builtins, "pd": pd, "plt": plt, "np": np}, 
            {"df": df})

    return answer_buffer.getvalue()

# Render HTML frontend
@app.route("/")
def serve_index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)