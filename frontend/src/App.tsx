import { useState, type FormEvent } from 'react'
import './App.css'

type CaseInput = {
  case_id: string
  attendance_rate: number | null
  missed_submissions: number | null
  engagement_status: string
  days_since_last_activity: number | null
  unresolved_support_tickets: number | null
}

type Evidence = {
  source?: string
  detail?: string
  value?: string | number | boolean | null
}

type AgentOutput = {
  agent_name: string
  status: string
  summary: string
  score: number
  flag: string
  evidence: Evidence[]
  output_data?: Record<string, unknown>
}

type Recommendation = {
  action: string
  priority_score: number
  priority_band: string
  reasons: string[]
  triggered_rules: string[]
  evidence: Evidence[]
  agent_output_refs: string[]
}

type WorkflowResult = {
  workflow_id: string
  student_case?: CaseInput
  agent_outputs: AgentOutput[]
  final_recommendation: Recommendation
  explanation: string | string[]
  audit_reference: string
  errors: string[]
}

const initialCase: CaseInput = {
  case_id: 'AA004-CASE-001',
  attendance_rate: 68,
  missed_submissions: 3,
  engagement_status: 'inactive',
  days_since_last_activity: 18,
  unresolved_support_tickets: 2,
}

const scenarios: { label: string; value: CaseInput }[] = [
  {
    label: 'Normal progress',
    value: {
      case_id: 'AA004-NORMAL-001',
      attendance_rate: 95,
      missed_submissions: 0,
      engagement_status: 'active',
      days_since_last_activity: 2,
      unresolved_support_tickets: 0,
    },
  },
  {
    label: 'Priority outreach',
    value: initialCase,
  },
  {
    label: 'Conflicting evidence',
    value: {
      case_id: 'AA004-CONFLICT-001',
      attendance_rate: 95,
      missed_submissions: 0,
      engagement_status: 'active',
      days_since_last_activity: 18,
      unresolved_support_tickets: 0,
    },
  },
  {
    label: 'Incomplete information',
    value: {
      case_id: 'AA004-INCOMPLETE-001',
      attendance_rate: null,
      missed_submissions: 1,
      engagement_status: 'unknown',
      days_since_last_activity: null,
      unresolved_support_tickets: 0,
    },
  },
]

const agentDescriptions: Record<string, string> = {
  'Case Intake Agent': 'Validates and normalizes the submitted case.',
  'Attendance Agent': 'Evaluates attendance indicators.',
  'Engagement Agent': 'Evaluates recent engagement and activity.',
  'Support Load Agent': 'Evaluates missed submissions and unresolved requests.',
  'Student Support Decision Agent': 'Combines evidence into a support recommendation.',
}

function App() {
  const [caseData, setCaseData] = useState<CaseInput>(initialCase)
  const [result, setResult] = useState<WorkflowResult | null>(null)
  const [audit, setAudit] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [auditLoading, setAuditLoading] = useState(false)
  const [error, setError] = useState('')

  function updateField<K extends keyof CaseInput>(key: K, value: CaseInput[K]) {
    setCaseData((current) => ({ ...current, [key]: value }))
  }

  function loadScenario(scenario: CaseInput) {
    setCaseData({ ...scenario })
    setResult(null)
    setAudit(null)
    setError('')
  }

  async function runWorkflow(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    setAudit(null)

    try {
      const response = await fetch('/api/workflows/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(caseData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : `Workflow request failed (${response.status})`,
        )
      }

      setResult(data as WorkflowResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to run workflow.')
    } finally {
      setLoading(false)
    }
  }

  async function loadAudit() {
    if (!result?.audit_reference) return

    setAuditLoading(true)
    setError('')

    try {
      const response = await fetch(
        `/api/audit/${encodeURIComponent(result.audit_reference)}`,
      )
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to retrieve audit record.')
      }

      setAudit(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Audit request failed.')
    } finally {
      setAuditLoading(false)
    }
  }

  const recommendation = result?.final_recommendation
  const actionClass = recommendation?.action.toLowerCase().replaceAll('_', '-')

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <strong>AA004</strong>
            <span>Student Support AI</span>
          </div>
        </div>

        <div className="side-label">WORKSPACE</div>
        <div className="nav-item active">
          <span>▦</span> Case prioritization
        </div>
        <div className="nav-item">
          <span>◎</span> Agent workflow
        </div>
        <div className="nav-item">
          <span>◷</span> Audit evidence
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Deterministic MVP</strong>
            <span>Phase 1.1 · Local environment</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">EDUCATION OPERATIONS / AA004</div>
            <h1>Student Support Prioritization</h1>
            <p>Evidence-led prioritization for timely academic support.</p>
          </div>
          <div className="top-status">
            <span className="status-dot" /> Workflow API
          </div>
        </header>

        <section className="overview-grid">
          <div className="overview-card">
            <span className="metric-label">WORKFLOW</span>
            <strong>5 agents</strong>
            <small>Specialized responsibilities</small>
          </div>
          <div className="overview-card">
            <span className="metric-label">DECISION MODEL</span>
            <strong>Rule-based</strong>
            <small>Deterministic evaluation</small>
          </div>
          <div className="overview-card">
            <span className="metric-label">EVIDENCE</span>
            <strong>Traceable</strong>
            <small>Reasons and audit references</small>
          </div>
        </section>

        <div className="workspace-grid">
          <section className="panel input-panel">
            <div className="panel-heading">
              <div>
                <span className="section-kicker">01 / CASE INTAKE</span>
                <h2>Student support case</h2>
                <p>Enter the available academic support indicators.</p>
              </div>
            </div>

            <div className="scenario-area">
              <label htmlFor="scenario">LOAD DEMO SCENARIO</label>
              <select
                id="scenario"
                defaultValue=""
                onChange={(event) => {
                  const selected = scenarios[Number(event.target.value)]
                  if (selected) loadScenario(selected.value)
                  event.target.value = ''
                }}
              >
                <option value="" disabled>Select a sample case</option>
                {scenarios.map((scenario, index) => (
                  <option key={scenario.label} value={index}>
                    {scenario.label}
                  </option>
                ))}
              </select>
            </div>

            <form onSubmit={runWorkflow}>
              <div className="form-field">
                <label htmlFor="case-id">CASE REFERENCE</label>
                <input
                  id="case-id"
                  value={caseData.case_id}
                  required
                  onChange={(e) => updateField('case_id', e.target.value)}
                />
              </div>

              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="attendance">ATTENDANCE (%)</label>
                  <input
                    id="attendance"
                    type="number"
                    min="0"
                    max="100"
                    value={caseData.attendance_rate ?? ''}
                    onChange={(e) =>
                      updateField(
                        'attendance_rate',
                        e.target.value === '' ? null : Number(e.target.value),
                      )
                    }
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="missed">MISSED SUBMISSIONS</label>
                  <input
                    id="missed"
                    type="number"
                    min="0"
                    value={caseData.missed_submissions ?? ''}
                    onChange={(e) =>
                      updateField(
                        'missed_submissions',
                        e.target.value === '' ? null : Number(e.target.value),
                      )
                    }
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="engagement">ENGAGEMENT STATUS</label>
                  <select
                    id="engagement"
                    value={caseData.engagement_status}
                    onChange={(e) => updateField('engagement_status', e.target.value)}
                  >
                    <option value="active">Active</option>
                    <option value="low">Low</option>
                    <option value="inactive">Inactive</option>
                    <option value="unknown">Unknown</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="days">DAYS SINCE LAST ACTIVITY</label>
                  <input
                    id="days"
                    type="number"
                    min="0"
                    value={caseData.days_since_last_activity ?? ''}
                    onChange={(e) =>
                      updateField(
                        'days_since_last_activity',
                        e.target.value === '' ? null : Number(e.target.value),
                      )
                    }
                  />
                </div>
                <div className="form-field full-width">
                  <label htmlFor="tickets">UNRESOLVED SUPPORT TICKETS</label>
                  <input
                    id="tickets"
                    type="number"
                    min="0"
                    value={caseData.unresolved_support_tickets ?? ''}
                    onChange={(e) =>
                      updateField(
                        'unresolved_support_tickets',
                        e.target.value === '' ? null : Number(e.target.value),
                      )
                    }
                  />
                </div>
              </div>

              <button className="primary-button" type="submit" disabled={loading}>
                {loading ? 'Running workflow…' : 'Run prioritization workflow →'}
              </button>
              <p className="form-note">
                The workflow evaluates support indicators only. It does not make
                grading, disciplinary or admission decisions.
              </p>
            </form>
          </section>

          <section className="panel result-panel">
            <div className="panel-heading">
              <div>
                <span className="section-kicker">02 / DECISION OUTPUT</span>
                <h2>Recommendation</h2>
                <p>Generated from the live workflow response.</p>
              </div>
              {result && <span className="live-tag">LIVE RESULT</span>}
            </div>

            {!result ? (
              <div className="empty-state">
                <div className="empty-icon">◎</div>
                <h3>Awaiting case evaluation</h3>
                <p>Submit a case to see its priority score, recommendation and evidence.</p>
              </div>
            ) : (
              <>
                <div className={`recommendation-card ${actionClass ?? ''}`}>
                  <span className="metric-label">FINAL RECOMMENDATION</span>
                  <h3>{recommendation?.action.replaceAll('_', ' ')}</h3>
                  <p>{recommendation?.priority_band} priority band</p>
                </div>

                <div className="score-row">
                  <div>
                    <span className="metric-label">PRIORITY SCORE</span>
                    <strong>{recommendation?.priority_score ?? 0}<small> / 100</small></strong>
                  </div>
                  <div className="score-track">
                    <div
                      className="score-fill"
                      style={{
                        width: `${Math.min(100, Math.max(0, recommendation?.priority_score ?? 0))}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="result-section">
                  <h4>Decision reasons</h4>
                  {recommendation?.reasons?.length ? (
                    <ul className="reason-list">
                      {recommendation.reasons.map((reason, index) => (
                        <li key={`${index}-${reason}`}>{reason}</li>
                      ))}
                    </ul>
                  ) : <p className="muted">No reasons returned.</p>}
                </div>

                <div className="result-section">
                  <h4>Triggered rules</h4>
                  <div className="tag-list">
                    {recommendation?.triggered_rules?.length
                      ? recommendation.triggered_rules.map((rule) => (
                          <span className="rule-tag" key={rule}>{rule}</span>
                        ))
                      : <span className="muted">No rule identifiers returned.</span>}
                  </div>
                </div>
              </>
            )}
          </section>
        </div>

        {error && <div className="error-banner">Request error: {error}</div>}

        {result && (
          <>
            <section className="panel agents-panel">
              <div className="panel-heading">
                <div>
                  <span className="section-kicker">03 / EXECUTION TRACE</span>
                  <h2>Agent workflow</h2>
                  <p>Actual agent outputs returned by the backend.</p>
                </div>
                <span className="count-tag">{result.agent_outputs.length} agents</span>
              </div>

              <div className="agent-list">
                {result.agent_outputs.map((agent, index) => (
                  <details className="agent-item" key={`${agent.agent_name}-${index}`}>
                    <summary>
                      <span className="agent-number">{String(index + 1).padStart(2, '0')}</span>
                      <span className="agent-info">
                        <strong>{agent.agent_name}</strong>
                        <small>{agentDescriptions[agent.agent_name] ?? agent.summary}</small>
                      </span>
                      <span className="agent-flag">{agent.flag || agent.status}</span>
                      <span className="expand-mark">＋</span>
                    </summary>
                    <div className="agent-details">
                      <p>{agent.summary}</p>
                      <div className="agent-meta">
                        <span>Status: <strong>{agent.status}</strong></span>
                        <span>Score: <strong>{agent.score}</strong></span>
                      </div>
                      <h4>Evidence</h4>
                      {agent.evidence?.length ? (
                        <ul className="reason-list">
                          {agent.evidence.map((item, i) => (
                            <li key={i}>
                              <strong>{item.source ?? 'Evidence'}:</strong> {item.detail}
                              {item.value !== undefined && item.value !== null
                                ? ` (${String(item.value)})` : ''}
                            </li>
                          ))}
                        </ul>
                      ) : <p className="muted">No evidence items returned.</p>}
                    </div>
                  </details>
                ))}
              </div>
            </section>

            <section className="lower-grid">
              <div className="panel">
                <span className="section-kicker">04 / EXPLANATION</span>
                <h2>Decision explanation</h2>
                {Array.isArray(result.explanation) ? (
                  <ul className="reason-list">
                    {result.explanation.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                ) : (
                  <p className="explanation-text">{result.explanation || 'No explanation returned.'}</p>
                )}
              </div>

              <div className="panel audit-panel">
                <span className="section-kicker">05 / AUDITABILITY</span>
                <h2>Audit record</h2>
                <p className="audit-reference">{result.audit_reference}</p>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={loadAudit}
                  disabled={auditLoading}
                >
                  {auditLoading ? 'Loading audit…' : 'Retrieve audit record'}
                </button>
                {audit !== null && (
                  <pre className="audit-json">{JSON.stringify(audit, null, 2)}</pre>
                )}
              </div>
            </section>

            <footer className="workflow-footer">
              <span>Workflow ID: {result.workflow_id}</span>
              <span>{result.errors.length} workflow errors</span>
            </footer>
          </>
        )}

        <footer className="page-footer">
          AA004 · Student Support Case Prioritization · Phase 1.1 MVP
        </footer>
      </main>
    </div>
  )
}

export default App
