# 🎙️ Meeting Summarizer

AI-powered meeting transcription and summarization application using Google Gemini 2.0 Flash API.

## ✨ Features

- 🎧 Audio & Video Transcription
- 🤖 AI-Powered Summarization
- ✅ Automatic Action Item Extraction
- 👥 Speaker Identification
- 📊 Key Decisions Highlighting
- 🌓 Dark/Light Mode
- 📥 Download Transcript & Summary

## 🛠️ Tech Stack

**Frontend:**
- React + Vite
- Axios
- CSS3

**Backend:**
- FastAPI
- Python 3.10+
- Google Generative AI (Gemini)
- Uvicorn

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm
- Google Gemini API Key (free at [ai.google.dev](https://ai.google.dev))

## 🚀 Local Installation & Setup

 1. Clone the Repository

git clone https://github.com/SmdFaraz/Meeting-Summarizer.git
cd Meeting-Summarizer


2. Backend Setup

Navigate to backend folder
cd backend

Create virtual environment
python -m venv venv

Activate virtual environment
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

Install dependencies
pip install -r requirements.txt

Create .env file
notepad .env # Windows

OR
touch .env # Mac/Linux

text

**Add this to `.env` file:**
GEMINI_API_KEY=your_gemini_api_key_here

text

Get your free API key from: https://ai.google.dev/

3. Frontend Setup

Open a **new terminal** and run:

Navigate to frontend folder
cd frontend

Install dependencies
npm install

Create .env file
notepad .env # Windows

OR
touch .env # Mac/Linux

text

**Add this to `.env` file:**
VITE_API_URL=http://localhost:8000

text

▶️ Running the Application

 Start Backend Server

**Terminal 1:**
cd backend
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux
python main.py

text

Backend will run at: [**http://localhost:8000**](http://localhost:8000)

### Start Frontend Server

**Terminal 2:**
cd frontend
npm run dev

text

Frontend will run at: [**http://localhost:5173**](http://localhost:5173)

### Access the Application

Open your browser and go to: [**http://localhost:5173**](http://localhost:5173)

## 📁 Supported File Formats

**Audio:**
- MP3
- WAV
- M4A
- FLAC

**Video:**
- MP4
- MOV
- AVI

**File Size:** Up to 2 GB  
**Duration:** Up to 9.5 hours

 🎯 Usage

1. Click on the upload box or drag and drop your meeting audio/video file
2. Click **"🚀 Start Processing"**
3. Wait for AI to transcribe and summarize (30-60 seconds for short files)
4. View results in **Transcript** and **Summary** tabs
5. Download transcript and summary as text files

## 📂 Project Structure
