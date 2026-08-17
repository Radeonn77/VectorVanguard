import { useEffect, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedSession, setSelectedSession] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState('')
  const [uploadError, setUploadError] = useState('')

  const [query, setQuery] = useState('')
  const [investigating, setInvestigating] = useState(false)
  const [investigationResult, setInvestigationResult] = useState('')
  const [investigationError, setInvestigationError] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/sessions`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to fetch sessions')
        }

        return response.json()
      })
      .then((data) => {
        setSessions(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0])
    setUploadResult('')
    setUploadError('')
  }

  const handleUpload = async () => {
    if (!selectedSession) {
      setUploadError('Please select an exam session.')
      return
    }

    if (!selectedFile) {
      setUploadError('Please select an image.')
      return
    }

    setUploading(true)
    setUploadResult('')
    setUploadError('')

    const formData = new FormData()

    formData.append(
      'session_id',
      selectedSession
    )

    formData.append(
      'file',
      selectedFile
    )

    try {
      const response = await fetch(
        `${API_URL}/upload-evidence`,
        {
          method: 'POST',
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Evidence upload failed.'
        )
      }

      setUploadResult(
        `Evidence uploaded successfully: ${data.evidence_id}`
      )

      setSelectedFile(null)

    } catch (err) {
      setUploadError(err.message)

    } finally {
      setUploading(false)
    }
  }

  const handleInvestigation = async () => {
    if (!query.trim()) {
      setInvestigationError(
        'Please enter an investigation question.'
      )
      return
    }

    setInvestigating(true)
    setInvestigationResult('')
    setInvestigationError('')

    try {
      const response = await fetch(
        `${API_URL}/investigate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: query.trim(),
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Investigation failed.'
        )
      }

      setInvestigationResult(data.answer)

    } catch (err) {
      setInvestigationError(err.message)

    } finally {
      setInvestigating(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>VectorVanguard</h1>
          <p>Offline AI Evidence Investigation System</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Local AI System
        </div>
      </header>

      <main className="dashboard">

        <section className="welcome">
          <h2>Evidence Investigation</h2>

          <p>
            Upload exam evidence and investigate it using
            the local AI pipeline.
          </p>
        </section>

        <section className="cards">

          {/* Evidence Upload */}

          <div className="card">
            <h3>Evidence Upload</h3>

            <p>
              Upload CCTV snapshots or exam-environment
              images for local processing.
            </p>

            <label>
              Exam Session
            </label>

            <select
              value={selectedSession}
              onChange={(event) =>
                setSelectedSession(event.target.value)
              }
            >
              <option value="">
                Select a session
              </option>

              {sessions.map((session) => (
                <option
                  key={session.id}
                  value={session.id}
                >
                  {session.exam_name}
                  {' '}
                  (Session {session.id})
                </option>
              ))}
            </select>

            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
            />

            <button
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading
                ? 'Processing...'
                : 'Upload Evidence'}
            </button>

            {uploadResult && (
              <p>
                {uploadResult}
              </p>
            )}

            {uploadError && (
              <p>
                Error: {uploadError}
              </p>
            )}
          </div>


          {/* Investigation */}

          <div className="card">
            <h3>Investigation</h3>

            <p>
              Ask questions about processed evidence using
              the local RAG system.
            </p>

            <textarea
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="Example: Was a mobile phone visible near the student's desk?"
              rows="4"
            />

            <button
              onClick={handleInvestigation}
              disabled={investigating}
            >
              {investigating
                ? 'Investigating...'
                : 'Investigate Evidence'}
            </button>

            {investigationResult && (
              <div className="result">
                <strong>AI Answer</strong>

                <p>
                  {investigationResult}
                </p>
              </div>
            )}

            {investigationError && (
              <p>
                Error: {investigationError}
              </p>
            )}
          </div>


          {/* Exam Sessions */}

          <div className="card">
            <h3>Exam Sessions</h3>

            <p>
              Sessions currently available in PostgreSQL:
            </p>

            {loading && (
              <p>Loading sessions...</p>
            )}

            {error && (
              <p>
                Error: {error}
              </p>
            )}

            {!loading && !error && (
              <div>
                {sessions.length === 0 ? (
                  <p>
                    No exam sessions found.
                  </p>
                ) : (
                  sessions.map((session) => (
                    <div key={session.id}>
                      <strong>
                        {session.exam_name}
                      </strong>

                      <p>
                        Session ID: {session.id}
                      </p>

                      <p>
                        Student ID: {session.student_id}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

        </section>

      </main>
    </div>
  )
}

export default App