from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import tempfile
import time
from pydantic import BaseModel
import traceback
import requests
import mimetypes
import sys

# Force unbuffered output so we can see prints
sys.stdout.reconfigure(line_buffering=True)

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

print(f"✅ API Key loaded: {api_key[:10]}...")

app = FastAPI(title="Meeting Summarizer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[  "https://meeting-summarizer.vercel.app",  # Your actual Vercel URL
        "http://localhost:5173" #For Local Deployment
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryRequest(BaseModel):
    transcript: str

@app.get("/")
def read_root():
    print("🏠 Root endpoint accessed")
    return {"message": "Meeting Summarizer API is running", "status": "online"}

def upload_to_gemini_manual(file_path: str, mime_type: str):
    """Manual upload using requests library"""
    print(f"\n🔧 Manual Upload Started")
    print(f"   File: {file_path}")
    print(f"   MIME: {mime_type}")
    
    # Step 1: Initiate upload
    url = "https://generativelanguage.googleapis.com/upload/v1beta/files"
    headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json"
    }
    
    metadata = {"file": {"display_name": os.path.basename(file_path)}}
    
    print(f"🌐 POST to: {url}")
    response = requests.post(f"{url}?key={api_key}", headers=headers, json=metadata)
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ❌ Error: {response.text}")
        raise Exception(f"Upload init failed: {response.text}")
    
    upload_url = response.headers.get('X-Goog-Upload-URL')
    print(f"✅ Upload URL obtained")
    
    # Step 2: Upload content
    print(f"📤 Uploading file content...")
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    headers = {
        "X-Goog-Upload-Command": "upload, finalize",
        "X-Goog-Upload-Offset": "0",
        "Content-Type": mime_type
    }
    
    response = requests.post(upload_url, headers=headers, data=file_data)
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ❌ Error: {response.text}")
        raise Exception(f"Upload failed: {response.text}")
    
    file_info = response.json()
    print(f"✅ Upload complete!")
    return file_info['file']

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file"""
    print("\n" + "="*50)
    print("🎬 NEW TRANSCRIBE REQUEST")
    print("="*50)
    
    tmp_path = None
    try:
        print(f"📁 File: {file.filename}")
        print(f"📦 Type: {file.content_type}")
        
        # Read content
        content = await file.read()
        size_mb = len(content) / 1024 / 1024
        print(f"📊 Size: {size_mb:.2f} MB ({len(content)} bytes)")
        
        # Save temp
        file_extension = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        print(f"💾 Saved: {tmp_path}")
        
        # MIME type
        mime_type = file.content_type
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file.filename)
            if not mime_type:
                mime_type = 'audio/mpeg'
        
        print(f"📝 MIME: {mime_type}")
        
        # Upload
        print("\n🚀 Starting upload...")
        file_info = upload_to_gemini_manual(tmp_path, mime_type)
        file_uri = file_info['uri']
        file_name = file_info['name']
        
        print(f"✅ URI: {file_uri}")
        print(f"✅ Name: {file_name}")
        
        # Wait for processing
        print("\n⏳ Waiting for processing...")
        max_wait = 120
        wait_time = 0
        
        while wait_time < max_wait:
            status_url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={api_key}"
            response = requests.get(status_url)
            
            if response.status_code != 200:
                print(f"❌ Status check failed: {response.text}")
                raise Exception(f"Status check failed: {response.text}")
            
            file_status = response.json()
            state = file_status.get('state', 'UNKNOWN')
            
            print(f"   {wait_time}s: {state}")
            
            if state == 'ACTIVE':
                print("✅ File is ACTIVE!")
                break
            elif state == 'FAILED':
                raise Exception("File processing FAILED")
            
            time.sleep(5)
            wait_time += 5
        
        if wait_time >= max_wait:
            raise HTTPException(status_code=504, detail="Timeout")
        
        # Generate transcript
        print("\n🎧 Generating transcript...")
        
        prompt = """Provide a detailed, accurate transcript with:
- All spoken words verbatim
- Speaker labels (Speaker 1, Speaker 2, etc.)
- Proper punctuation and formatting
- Clear paragraph breaks"""
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"file_data": {"mime_type": mime_type, "file_uri": file_uri}}
                ]
            }]
        }
        
        print("🤖 Calling Gemini API...")
        api_response = requests.post(api_url, json=payload)
        
        print(f"   Status: {api_response.status_code}")
        
        if api_response.status_code != 200:
            print(f"❌ API Error: {api_response.text}")
            raise Exception(f"API failed: {api_response.text}")
        
        result = api_response.json()
        
        # Extract transcript
        try:
            transcript = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Transcript: {len(transcript)} characters")
        except (KeyError, IndexError) as e:
            print(f"❌ Parse error: {result}")
            raise Exception(f"Parse error: {e}")
        
        # Cleanup
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print("🧹 Temp file deleted")
        
        print("\n✅✅✅ SUCCESS! ✅✅✅\n")
        
        return {
            "success": True,
            "transcript": transcript,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌❌❌ ERROR ❌❌❌")
        print(f"Error: {str(e)}")
        print(f"Type: {type(e).__name__}")
        print(f"\nTraceback:")
        print(traceback.format_exc())
        
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summarize")
async def summarize_transcript(request: SummaryRequest):
    """Generate summary"""
    print("\n📊 Summarize request received")
    try:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        prompt = f"""Create a professional meeting summary:

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
{request.transcript}"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(api_url, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API failed: {response.text}")
        
        result = response.json()
        summary = result['candidates'][0]['content']['parts'][0]['text']
        
        print(f"✅ Summary: {len(summary)} characters")
        
        return {"success": True, "summary": summary}
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
