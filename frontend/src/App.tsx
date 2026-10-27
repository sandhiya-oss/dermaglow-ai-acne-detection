
import { useState } from 'react'
import './App.css'
import Progress from './Progress'
import Routine from './Routine'
import Journal from './Journal'
import Products from './Products'
import AcneAnalysis from './AcneAnalysis'

const features = [
  { icon: '◉', title: 'Acne Analysis', description: 'Analyze acne severity with your AI model.', tag: 'AI POWERED' },
  { icon: '♡', title: 'Daily Routine', description: 'Keep your morning and evening skincare organized.', tag: 'YOUR ROUTINE' },
  { icon: '↗', title: 'Skin Progress', description: 'Track your skincare journey over time.', tag: 'INSIGHTS' },
]

function App() {
  const [active, setActive] = useState('Overview')
  const [imageName, setImageName] = useState('')
  const [preview, setPreview] = useState('')
  const [message, setMessage] = useState('')

  function handleImage(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setMessage('Please select an image file.')
      return
    }

    setImageName(file.name)
    setPreview(URL.createObjectURL(file))
    setMessage('Image selected. For model analysis, open the Acne Analysis page.')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#">
          <span className="brand-mark">d.</span>
          <span>dermaglow<span className="brand-ai"> AI</span><small>YOUR PERSONAL SKIN SPACE</small></span>
        </a>

        <p className="nav-label">WORKSPACE</p>

        {['Overview', 'Acne Analysis', 'Daily Routine', 'Skin Progress', 'Skin Journal', 'Product Explorer'].map((item, index) => (
          <button
            key={item}
            className={`nav-item ${active === item ? 'selected' : ''}`}
            onClick={() => setActive(item)}
          >
            <span className="nav-icon">{['⌂', '◉', '♡', '↗', '▤', '✧'][index]}</span>
            {item}
          </button>
        ))}

        <div className="sidebar-bottom">
          <div className="privacy-icon">✳</div>
          <strong>Your skin. Your journey.</strong>
          <p>Personalized guidance, one day at a time.</p>
          <span className="privacy-tag">◉ &nbsp; PRIVACY MATTERS</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {active}</div>
          <div className="topbar-right">
            <span className="status-dot" /> YOUR SKINCARE SPACE
            <div className="avatar">D</div>
          </div>
        </header>

        <section className="welcome-section">
          <div>
            <p className="eyebrow">YOUR PERSONAL SKINCARE COMPANION</p>
            <h1>A little care.<br /><span>A lot of glow.</span></h1>
            <p className="welcome-copy">
              Get to know your skin, build consistent habits, and celebrate your progress — one day at a time.
            </p>
            <button className="primary-button" onClick={() => setActive('Acne Analysis')}>
              Explore skin analysis <span>↗</span>
            </button>
          </div>

          <div className="hero-art">
            <div className="sun-circle" />
            <div className="hero-orbit orbit-one" />
            <div className="hero-orbit orbit-two" />
            <div className="hero-flower">✿</div>
            <div className="hero-caption">
              <span>01 / YOUR JOURNEY</span>
              <strong>Feel good in your skin.</strong>
            </div>
          </div>
        </section>

        <div className="section-heading">
          <div>
            <p className="eyebrow">YOUR SPACE, YOUR PACE</p>
            <h2>Your skincare workspace</h2>
          </div>
          <span className="subtle-label">MADE FOR YOUR JOURNEY</span>
        </div>

        <section className="feature-grid">
          {features.map((feature) => (
            <button
              className="feature-card"
              key={feature.title}
              onClick={() => setActive(
                feature.title === 'Acne Analysis'
                  ? 'Acne Analysis'
                  : feature.title === 'Daily Routine'
                    ? 'Daily Routine'
                    : 'Skin Progress'
              )}
            >
              <span className="feature-icon">{feature.icon}</span>
              <span className="feature-tag">{feature.tag}</span>
              <strong>{feature.title}</strong>
              <span className="feature-description">{feature.description}</span>
              <span className="card-link">Explore feature <span>↗</span></span>
            </button>
          ))}
        </section>

        {active === 'Acne Analysis' ? (
          <AcneAnalysis />
        ) : active === 'Product Explorer' ? (
          <Products />
        ) : active === 'Skin Journal' ? (
          <Journal />
        ) : active === 'Daily Routine' ? (
          <Routine />
        ) : active === 'Skin Progress' ? (
          <Progress />
        ) : active === 'Overview' ? (
          <section className="analysis-panel">
            <div className="analysis-copy">
              <p className="eyebrow">A GENTLE FIRST STEP</p>
              <h2>Let's get to know<br />your skin.</h2>
              <p>
                Choose a clear facial image to preview it here. To submit an image to your trained model, open Acne Analysis from the sidebar.
              </p>

              <label className="primary-button upload-button">
                Choose an image <span>↑</span>
                <input type="file" accept="image/*" onChange={handleImage} hidden />
              </label>

              {imageName && <p className="file-name">Selected: {imageName}</p>}
              {message && <p className="notice">{message}</p>}
            </div>

            <div className="image-preview">
              {preview ? (
                <img src={preview} alt="Selected facial image preview" />
              ) : (
                <div className="upload-placeholder">
                  <span>＋</span>
                  <strong>Your skin, your story</strong>
                  <small>Image preview appears here</small>
                </div>
              )}
              <span className="preview-label">IMAGE PREVIEW</span>
            </div>
          </section>
        ) : (
          <section className="analysis-panel section-placeholder">
            <p className="eyebrow">COMING TO YOUR WORKSPACE</p>
            <h2>{active}</h2>
            <p>This section is part of your DermaGlow AI workspace. We'll add its working features step by step.</p>
            <button className="secondary-button" onClick={() => setActive('Overview')}>
              ← Back to overview
            </button>
          </section>
        )}

        <footer>
          <span>dermaglow AI © 2026</span>
          <span>Built with care <span className="footer-heart">♥</span> for your skin journey</span>
        </footer>
      </main>
    </div>
  )
}

export default App
