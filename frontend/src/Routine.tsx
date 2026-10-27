import { useEffect, useState } from 'react'

type RoutineTask = {
  id: string
  label: string
  done: boolean
}

const morningDefaults: RoutineTask[] = [
  { id: 'cleanse', label: 'Gentle cleanser', done: false },
  { id: 'moisturize', label: 'Moisturizer', done: false },
  { id: 'sunscreen', label: 'Broad-spectrum sunscreen', done: false },
]

const eveningDefaults: RoutineTask[] = [
  { id: 'evening-cleanse', label: 'Gentle cleanser', done: false },
  { id: 'evening-moisturize', label: 'Moisturizer', done: false },
]

function getTodayKey() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `dermaglow-routine-${year}-${month}-${day}`
}

function loadTasks(): RoutineTask[] {
  try {
    const saved = localStorage.getItem(getTodayKey())
    if (saved) return JSON.parse(saved) as RoutineTask[]
  } catch {
    // Use the default checklist if saved data cannot be read.
  }
  return [...morningDefaults, ...eveningDefaults]
}

export default function Routine() {
  const [tasks, setTasks] = useState<RoutineTask[]>(loadTasks)

  useEffect(() => {
    localStorage.setItem(getTodayKey(), JSON.stringify(tasks))
  }, [tasks])

  const completed = tasks.filter((task) => task.done).length
  const percentage = Math.round((completed / tasks.length) * 100)

  function toggleTask(id: string) {
    setTasks((current) =>
      current.map((task) =>
        task.id === id ? { ...task, done: !task.done } : task
      )
    )
  }

  function resetTasks() {
    setTasks([...morningDefaults, ...eveningDefaults])
  }

  return (
    <section className="routine-page">
      <p className="eyebrow">YOUR DAILY SELF-CARE</p>
      <h2 className="progress-title">Consistency over perfection.</h2>
      <p className="progress-intro">
        A gentle routine can help you build steady habits. Adjust these example
        steps to suit your skin and any guidance from your healthcare professional.
      </p>

      <article className="routine-summary">
        <div>
          <span className="routine-overline">TODAY'S PROGRESS</span>
          <h3>{completed} of {tasks.length} steps completed</h3>
          <p>{percentage === 100 ? 'Lovely work — your checklist is complete!' : 'Every small step counts. Go at your own pace.'}</p>
        </div>
        <div className="routine-percent">{percentage}%</div>
        <div className="routine-progress-track">
          <div className="routine-progress-fill" style={{ width: `${percentage}%` }} />
        </div>
      </article>

      <div className="routine-columns">
        <article className="routine-card">
          <div className="routine-card-heading">
            <span className="routine-symbol">☀</span>
            <div>
              <h3>Morning routine</h3>
              <p>A fresh start for your day</p>
            </div>
          </div>
          {tasks.filter((task) => morningDefaults.some((item) => item.id === task.id)).map((task) => (
            <label className={`routine-task ${task.done ? 'task-done' : ''}`} key={task.id}>
              <input type="checkbox" checked={task.done} onChange={() => toggleTask(task.id)} />
              <span>{task.label}</span>
            </label>
          ))}
        </article>

        <article className="routine-card">
          <div className="routine-card-heading">
            <span className="routine-symbol evening-symbol">☾</span>
            <div>
              <h3>Evening routine</h3>
              <p>Wind down gently</p>
            </div>
          </div>
          {tasks.filter((task) => eveningDefaults.some((item) => item.id === task.id)).map((task) => (
            <label className={`routine-task ${task.done ? 'task-done' : ''}`} key={task.id}>
              <input type="checkbox" checked={task.done} onChange={() => toggleTask(task.id)} />
              <span>{task.label}</span>
            </label>
          ))}
        </article>
      </div>

      <div className="routine-tip">
        <span>✿</span>
        <div>
          <strong>A gentle reminder</strong>
          <p>Introduce new products gradually, follow their labels, and stop using a product if it causes significant irritation. This tracker is for habits, not medical advice.</p>
        </div>
      </div>

      <button className="secondary-button routine-reset" onClick={resetTasks}>
        Reset today's checklist
      </button>
    </section>
  )
}
