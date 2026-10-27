
import { useState } from 'react'

type Prediction = {
  predicted_level: number
  predicted_label: string
  model_score_percent: number
  class_scores_percent: Record<string, number>
  device: string
  notice: string
}

export default function AcneAnalysis() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState('')
  const [result, setResult] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function selectImage(selected?: File) {
    if (!selected) return

    if (!selected.type.startsWith('image/')) {
      setError('Please select an image file.')
      return
    }

    if (preview) URL.revokeObjectURL(preview)

    setFile(selected)
    setPreview(URL.createObjectURL(selected))
    setResult(null)
    setError('')
  }

  async function analyzeImage() {
    if (!file) {
      setError('Please choose an image first.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://127.0.0.1:8001/predict', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Image analysis failed.')
      }

      setResult(data as Prediction)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not connect to the backend.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="analysis-page">
      <div className="analysis-heading">
        <p className="analysis-eyebrow">DERMAGLOW AI</p>
        <h1>Acne Analysis</h1>
        <p>
          Upload a skin image to receive an estimate from your trained model.
        </p>
      </div>

      <div className="analysis-card">
        <label className="upload-area">
          {preview ? (
            <img
              className="analysis-preview"
              src={preview}
              alt="Selected skin image preview"
            />
          ) : (
            <div className="upload-placeholder">
              <span className="upload-icon">＋</span>
              <strong>Choose an image</strong>
              <span>Click here to select an image from your device</span>
            </div>
          )}

          <input
            type="file"
            accept="image/*"
            onChange={(event) => selectImage(event.target.files?.[0])}
          />
        </label>

        <button
          className="analyze-button"
          onClick={analyzeImage}
          disabled={!file || loading}
        >
          {loading ? 'Analyzing image...' : 'Analyze Image'}
        </button>

        {error && <p className="analysis-error">{error}</p>}
      </div>

      {result && (
        <div className="analysis-result">
          <p className="analysis-eyebrow">MODEL RESULT</p>
          <h2>{result.predicted_label}</h2>
          <p>Model score: {result.model_score_percent.toFixed(2)}%</p>

          <h3>Scores by level</h3>

          {Object.entries(result.class_scores_percent).map(
            ([label, score]) => (
              <div className="score-row" key={label}>
                <div className="score-label">
                  <span>{label}</span>
                  <span>{score.toFixed(2)}%</span>
                </div>
                <div className="score-track">
                  <div
                    className="score-fill"
                    style={{
                      width: `${Math.min(100, Math.max(0, score))}%`,
                    }}
                  />
                </div>
              </div>
            )
          )}

          <p className="analysis-notice">{result.notice}</p>
        </div>
      )}

      <p className="analysis-disclaimer">
        This is an educational model estimate, not a medical diagnosis.
        Results may be inaccurate.
      </p>
    </section>
  )
}
