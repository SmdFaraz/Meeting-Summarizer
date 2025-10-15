import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [summary, setSummary] = useState('')
  const [activeTab, setActiveTab] = useState('transcript')
  const [isDark, setIsDark] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || window.location.origin.replace('5173', '8000')

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setTranscript('')
    setSummary('')
  }

  const handleProcess = async () => {
    if (!file) {
      alert('Please select a file first')
      return
    }

    setLoading(true)
    setProgress(0)

    try {
      // Step 1: Transcribe
      setProgress(25)
      const formData = new FormData()
      formData.append('file', file)

      const transcribeRes = await axios.post(`${API_URL}/api/transcribe`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setTranscript(transcribeRes.data.transcript)
      setProgress(60)

      // Step 2: Summarize
      const summaryRes = await axios.post(`${API_URL}/api/summarize`, {
        transcript: transcribeRes.data.transcript
      })

      setSummary(summaryRes.data.summary)
      setProgress(100)

    } catch (error) {
      console.error('Error:', error)
      alert('Processing failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const downloadTranscript = () => {
    const blob = new Blob([transcript], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'transcript.txt'
    a.click()
  }

  const downloadSummary = () => {
    const blob = new Blob([summary], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'summary.txt'
    a.click()
  }

  return (
    <div className={isDark ? 'app dark' : 'app'}>
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="title">Meeting Summarizer</h1>
          <button 
            className="theme-toggle"
            onClick={() => setIsDark(!isDark)}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          
          {/* Upload Section */}
          <section className="upload-section">
            <div className="upload-box">
              <input
                type="file"
                id="file-upload"
                accept="audio/*,video/*"
                onChange={handleFileChange}
                className="file-input"
              />
              <label htmlFor="file-upload" className="file-label">
                <div className="upload-icon">📁</div>
                <p className="upload-text">
                  {file ? file.name : 'Choose audio or video file'}
                </p>
                <p className="upload-hint">MP3, WAV, MP4, MOV • Max 2GB</p>
              </label>
            </div>

            {file && (
              <button 
                className="process-btn"
                onClick={handleProcess}
                disabled={loading}
              >
                {loading ? 'Processing...' : '🚀 Start Processing'}
              </button>
            )}

            {loading && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="progress-text">{progress}% Complete</p>
              </div>
            )}
          </section>

          {/* Results Section */}
          {transcript && (
            <section className="results-section">
              <div className="tabs">
                <button 
                  className={`tab ${activeTab === 'transcript' ? 'active' : ''}`}
                  onClick={() => setActiveTab('transcript')}
                >
                  📝 Transcript
                </button>
                <button 
                  className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
                  onClick={() => setActiveTab('summary')}
                >
                  📊 Summary
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'transcript' && (
                  <div className="result-box">
                    <div className="result-header">
                      <h3>Full Transcript</h3>
                      <button className="download-btn" onClick={downloadTranscript}>
                        ⬇️ Download
                      </button>
                    </div>
                    <div className="result-text">{transcript}</div>
                  </div>
                )}

                {activeTab === 'summary' && summary && (
                  <div className="result-box">
                    <div className="result-header">
                      <h3>AI Summary</h3>
                      <button className="download-btn" onClick={downloadSummary}>
                        ⬇️ Download
                      </button>
                    </div>
                    <div className="result-text markdown">{summary}</div>
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Powered by Google Gemini AI • Built with React & FastAPI</p>
      </footer>
    </div>
  )
}

export default App
