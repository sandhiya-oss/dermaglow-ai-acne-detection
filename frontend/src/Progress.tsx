import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
} from 'recharts'

const progressData = [
  { week: 'Week 1', score: 4 },
  { week: 'Week 2', score: 3 },
  { week: 'Week 3', score: 3.5 },
  { week: 'Week 4', score: 2.5 },
]

const routineData = [
  { day: 'Mon', completed: 2 },
  { day: 'Tue', completed: 1 },
  { day: 'Wed', completed: 2 },
  { day: 'Thu', completed: 1 },
  { day: 'Fri', completed: 2 },
  { day: 'Sat', completed: 0 },
  { day: 'Sun', completed: 1 },
]

export default function Progress() {
  return (
    <section className="progress-page">
      <p className="eyebrow">YOUR PERSONAL SKINCARE JOURNEY</p>
      <h2 className="progress-title">Small steps, meaningful habits.</h2>
      <p className="progress-intro">
        Your space to reflect on your routine and track your journey over time.
        The charts below contain sample data until you record your own progress.
      </p>

      <div className="progress-stats">
        <article className="progress-stat">
          <span>ROUTINE TRACKER</span>
          <strong>7 days</strong>
          <small>A weekly overview</small>
        </article>
        <article className="progress-stat">
          <span>DAILY CHECK-IN</span>
          <strong>2 steps</strong>
          <small>Morning and evening</small>
        </article>
        <article className="progress-stat">
          <span>YOUR NEXT STEP</span>
          <strong>Stay consistent</strong>
          <small>Progress takes time</small>
        </article>
      </div>

      <div className="progress-chart-grid">
        <article className="chart-card">
          <p className="eyebrow">ILLUSTRATIVE DATA</p>
          <h3>Weekly skin journal</h3>
          <p className="chart-description">
            Example ratings on a 1–5 scale, not actual skin measurements.
          </p>
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={progressData} margin={{ top: 12, right: 12, left: -18, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee2dd" />
                <XAxis dataKey="week" tick={{ fontSize: 10 }} />
                <YAxis domain={[1, 5]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="score"
                  name="Sample rating"
                  stroke="#ad7778"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#ad7778' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="chart-card">
          <p className="eyebrow">ILLUSTRATIVE DATA</p>
          <h3>Weekly routine activity</h3>
          <p className="chart-description">
            Example completed skincare steps per day.
          </p>
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={routineData} margin={{ top: 12, right: 8, left: -18, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eee2dd" />
                <XAxis dataKey="day" tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} domain={[0, 2]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="completed" name="Sample steps" fill="#d6aaa0" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </div>

      <div className="journal-note">
        <span className="note-icon">✿</span>
        <div>
          <h3>Your journey is personal</h3>
          <p>
            These are demonstration charts only. They do not represent an actual
            acne diagnosis or measured improvement. We'll add saved personal
            entries in a later step.
          </p>
        </div>
      </div>
    </section>
  )
}
