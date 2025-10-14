from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv
import tempfile
import time
from pydantic import BaseModel

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

app = FastAPI(title="Meeting Summarizer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryRequest(BaseModel):
    transcript: str

@app.get("/")
def read_root():
    return {"message": "Meeting Summarizer API is running", "status": "online"}

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file using Gemini AI"""
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Upload to Gemini
        gemini_file = genai.upload_file(tmp_path)
        
        # Wait for processing
        while gemini_file.state.name == "PROCESSING":
            time.sleep(2)
            gemini_file = genai.get_file(gemini_file.name)
        
        if gemini_file.state.name == "FAILED":
            raise HTTPException(status_code=500, detail="File processing failed")
        
        # Generate transcript
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        transcript_prompt = """
Provide a detailed, accurate transcript with:
- All spoken words verbatim
- Speaker labels (Speaker 1, Speaker 2, etc.)
- Proper punctuation and formatting
- Clear paragraph breaks
"""
        
        response = model.generate_content([transcript_prompt, gemini_file])
        transcript = response.text
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "transcript": transcript,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summarize")
async def summarize_transcript(request: SummaryRequest):
    """Generate summary from transcript"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        summary_prompt = f"""
Create a professional meeting summary:

## 📌 Key Decisions
- Important decisions made

## ✅ Action Items
- Task: Person - Deadline

## 💬 Discussion Topics
- Main topics discussed

## 🎯 Next Steps
- Follow-up actions

## 👥 Participants
- People mentioned

## ⭐ Highlights
- Important moments

TRANSCRIPT:
{request.transcript}
"""
        
        response = model.generate_content(summary_prompt)
        summary = response.text
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
