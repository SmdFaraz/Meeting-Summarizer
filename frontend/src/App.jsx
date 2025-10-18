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
  const [error, setError] = useState('')

  const API_URL = import.meta.env.VITE_API_URL || window.location.origin.replace('5173', '8000')

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setTranscript('')
    setSummary('')
    setError('')
  }

  const handleProcess = async () => {
    if (!file) {
      alert('Please select a file first')
      return
    }

    setLoading(true)
    setProgress(0)
    setError('')

    try {
      console.log('🚀 Starting process...')
      console.log('📁 File:', file.name)
      console.log('🌐 API URL:', API_URL)

      // Step 1: Transcribe with longer timeout
      setProgress(10)
      const formData = new FormData()
      formData.append('file', file)

      console.log('📤 Uploading to API...')

      const transcribeRes = await axios.post(`${API_URL}/api/transcribe`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000, // 5 minutes timeout
        onUploadProgress: (progressEvent) => {
          const uploadPercent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setProgress(Math.min(uploadPercent * 0.3, 30)) // 0-30% for upload
          console.log(`📊 Upload: ${uploadPercent}%`)
        }
      })

      console.log('✅ Transcribe response:', transcribeRes.data)

      if (!transcribeRes.data.transcript) {
        throw new Error('No transcript received from server')
      }

      setTranscript(transcribeRes.data.transcript)
      setProgress(60)
      console.log('✅ Transcript received!')

      // Step 2: Summarize
      console.log('📊 Generating summary...')
      setProgress(70)

      const summaryRes = await axios.post(`${API_URL}/api/summarize`, {
        transcript: transcribeRes.data.transcript
      }, {
        timeout: 120000 // 2 minutes for summary
      })

      console.log('✅ Summary response:', summaryRes.data)

      if (!summaryRes.data.summary) {
        throw new Error('No summary received from server')
      }

      setSummary(summaryRes.data.summary)
      setProgress(100)
      console.log('✅✅✅ All done!')

    } catch (error) {
      console.error('❌ Error:', error)
      console.error('❌ Error response:', error.response?.data)
      
      let errorMessage = 'Processing failed. Please try again.'
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout. File might be too large or server is slow.'
      } else if (error.response) {
        errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setError(errorMessage)
      alert(errorMessage)
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
    URL.revokeObjectURL(url)
  }

  const downloadSummary = () => {
    const blob = new Blob([summary], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'summary.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className={isDark ? 'app dark' : 'app'}>
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="title">🎙️ Meeting Summarizer</h1>
          <button 
            className="theme-toggle"
            onClick={() => setIsDark(!isDark)}
            aria-label="Toggle theme"
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
                disabled={loading}
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
                {loading ? '⏳ Processing...' : '🚀 Start Processing'}
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
                <p className="progress-text">
                  {progress}% Complete
                  {progress < 30 && ' - Uploading...'}
                  {progress >= 30 && progress < 60 && ' - Transcribing...'}
                  {progress >= 60 && progress < 100 && ' - Summarizing...'}
                  {progress === 100 && ' - Done! ✅'}
                </p>
              </div>
            )}

            {error && (
              <div className="error-message">
                ❌ {error}
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
                  disabled={!summary}
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

                {activeTab === 'summary' && !summary && (
                  <div className="result-box">
                    <p>⏳ Generating summary...</p>
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Powered by Google Gemini AI 🤖</p>
      </footer>
    </div>
  )
}

export default App
