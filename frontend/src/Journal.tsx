import { useEffect, useState } from 'react'

type JournalEntry = {
  id: string
  date: string
  mood: string
  concern: string
  notes: string
}

const STORAGE_KEY = 'dermaglow-skin-journal'

export default function Journal() {
  const [entries, setEntries] = useState<JournalEntry[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    } catch {
      return []
    }
  })

  const [mood, setMood] = useState('Feeling good')
  const [concern, setConcern] = useState('Breakouts')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries))
  }, [entries])

  function saveEntry() {
    if (!notes.trim()) {
      alert('Please add a few notes before saving your entry.')
      return
    }

    const entry: JournalEntry = {
      id: `${Date.now()}`,
      date: new Date().toLocaleString(),
      mood,
      concern,
      notes: notes.trim(),
    }

    setEntries((current) => [entry, ...current])
    setNotes('')
  }

  function deleteEntry(id: string) {
    setEntries((current) => current.filter((entry) => entry.id !== id))
  }

  return (
    <section className="journal-page">
      <p className="eyebrow">YOUR PERSONAL SKIN DIARY</p>
      <h2 className="progress-title">A little note to yourself.</h2>
      <p className="progress-intro">
        Record your observations and notice patterns over time. Skin changes
        naturally from day to day.
      </p>

      <div className="journal-layout">
        <article className="journal-form">
          <h3>Today's skin note</h3>
          <p className="journal-subtitle">Take a moment to check in with yourself.</p>

          <label className="journal-label" htmlFor="skin-mood">
            How is your skin feeling?
          </label>
          <select
            id="skin-mood"
            value={mood}
            onChange={(event) => setMood(event.target.value)}
          >
            <option>Feeling good</option>
            <option>A little dry</option>
            <option>Feeling oily</option>
            <option>Sensitive today</option>
            <option>Not sure</option>
          </select>

          <label className="journal-label" htmlFor="skin-concern">
            Main observation
          </label>
          <select
            id="skin-concern"
            value={concern}
            onChange={(event) => setConcern(event.target.value)}
          >
            <option>Breakouts</option>
            <option>Dryness</option>
            <option>Oiliness</option>
            <option>Redness or irritation</option>
            <option>Skin feels unchanged</option>
            <option>Other observation</option>
          </select>

          <label className="journal-label" htmlFor="skin-notes">
            Notes
          </label>
          <textarea
            id="skin-notes"
            rows={5}
            placeholder="What did you notice today? Any new products or changes in your routine?"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
          />

          <button className="journal-save" onClick={saveEntry}>
            Save journal entry
          </button>
        </article>

        <article className="journal-history">
          <div className="journal-history-heading">
            <div>
              <h3>Your journal</h3>
              <p className="journal-subtitle">
                {entries.length} {entries.length === 1 ? 'entry' : 'entries'} saved
              </p>
            </div>
            <span className="journal-flower">✿</span>
          </div>

          {entries.length === 0 ? (
            <div className="journal-empty">
              <span>♡</span>
              <h4>Your story starts here</h4>
              <p>Your saved skin observations will appear here.</p>
            </div>
          ) : (
            <div className="journal-entries">
              {entries.map((entry) => (
                <article className="journal-entry" key={entry.id}>
                  <div className="journal-entry-top">
                    <span className="journal-entry-date">{entry.date}</span>
                    <button
                      className="journal-delete"
                      onClick={() => deleteEntry(entry.id)}
                      aria-label="Delete journal entry"
                      title="Delete entry"
                    >
                      ×
                    </button>
                  </div>
                  <div className="journal-tags">
                    <span>{entry.mood}</span>
                    <span>{entry.concern}</span>
                  </div>
                  <p className="journal-entry-notes">{entry.notes}</p>
                </article>
              ))}
            </div>
          )}
        </article>
      </div>

      <p className="journal-privacy">
        Your entries are stored in this browser on this device. They are not
        synced to an account or medical record.
      </p>
    </section>
  )
}
