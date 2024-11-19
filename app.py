# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import anthropic

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    query: str
    company_ticker: str

class Answer(BaseModel):
    response: str
    sources: List[str]

@app.get("/")
def read_root():
    return {"status": "API is running"}

@app.post("/answer", response_model=Answer)
async def get_answer(request: QuestionRequest):
    try:
        client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        prompt = f"""Given the company {request.company_ticker}, please answer the following question:
        {request.query}
        
        Base your answer only on verified company information. If you're unsure, please state that clearly.
        """
        
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return Answer(
            response=message.content,
            sources=["SEC Filings", "Company Website"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
