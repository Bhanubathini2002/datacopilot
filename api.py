import os
from fastapi import FastAPI
from typing import Dict, Any
import json
import uuid
import subprocess
from opendataqna import executeqna

load_dotenv()
app = FastAPI()
#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"bhanu": "prakash"}

# @app.get("/ram")
# def ram():
#     resp = client.responses.create(
#         model="gpt-4o-mini",
#         input="Say hello in one big passage sentence."
#     )
#     return {"reply": resp.output_text}

@app.get("/qna")
def ask_open_data_qna(
    question: str,
    user_grouping: str
) -> Dict[str, Any]:
    """
    Ask a question against Open_Data_QnA.

    Args:
        question: NL question from the user
        user_grouping: dataset/schema identifier (e.g. "MovieExplorer-bigquery")
        execute_sql: run the final SQL if True, or only generate SQL if False

    Returns:
        A JSON object with the raw output plus some context.
    """

    raw_output =  executeqna(
        question=question,
        user_grouping=user_grouping
        
    )

    # If your opendataqna.py prints JSON, you can parse it.
    # If not, we just wrap the raw text.
    try:
         
        # parsed = json.loads(raw_output)
         parsed = raw_output.to_dict(orient="records")
    except Exception:
        parsed = {"raw_output": raw_output}

    return {
        "question": question,
        "user_grouping": user_grouping,
        "result": parsed,
    }

import uvicorn 
if  __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)