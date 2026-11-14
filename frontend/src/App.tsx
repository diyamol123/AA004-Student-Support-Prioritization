import { useEffect, useState, type FormEvent } from 'react'
import './App.css'

type CaseInput = {
  case_id: string
  attendance_rate: number | null
  missed_submissions: number | null
  engagement_status: string
  days_since_last_activity: number | null
  unresolved_support_tickets: number | null
  recent_activity_indicators: string[]
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

type ValidatedCase = {
  case_id: string
  attendance_rate: number | null
  missed_submissions: number | null
  engagement_status: string | null
  days_since_last_activity: number | null
  unresolved_support_tickets: number | null
  recent_activity_indicators: string[]
  missing_fields: string[]
}

type WorkflowResult = {
  workflow_id: string
  student_case: CaseInput
  validated_case?: ValidatedCase | null
  attendance_flag: string | null
  engagement_flag: string | null
  support_load_flag: string | null
  scores: Record<string, number>
  agent_outputs: AgentOutput[]
  node_trace?: string[]
  final_recommendation: Recommendation | null
  explanation: string | string[]
  llm_metadata?: {
    llm_used: boolean
    provider: string
    model: string
    status: string
    fallback_used: boolean
    validation_status: string
    error_category?: string | null
  }
  audit_reference: string | null
  errors: string[]
  created_at: string
}

const initialCase: CaseInput = {
  case_id: 'AA004-CASE-001',
  attendance_rate: 68,
  missed_submissions: 3,
  engagement_status: 'inactive',
  days_since_last_activity: 18,
  unresolved_support_tickets: 2,
  recent_activity_indicators: [],
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
      recent_activity_indicators: [],
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
      recent_activity_indicators: [],
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
      recent_activity_indicators: [],
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

const evidenceSourceLabels: Record<string, string> = {
  'student_case.attendance_rate': 'Attendance indicator',
  'student_case.days_since_last_activity': 'Recent activity',
  'student_case.engagement_status': 'Engagement indicator',
  'student_case.missed_submissions': 'Missed submissions',
  'student_case.unresolved_support_tickets': 'Open support requests',
  attendance_demo_thresholds: 'Attendance guidance',
  engagement_demo_thresholds: 'Activity guidance',
  support_load_demo_thresholds: 'Support-load guidance',
  decision_agent: 'Decision evidence',
}

const intakeEvidenceLabels: Record<string, string> = {
  attendance_rate: 'Attendance information',
  missed_submissions: 'Submission information',
  engagement_status: 'Engagement information',
  unresolved_support_tickets: 'Support request information',
}

function getEvidenceSourceLabel(source: string, detail = ''): string {
  if (source === 'student_case') {
    const field = detail.match(/^([a-z_]+) was supplied$/)?.[1]
    return field ? intakeEvidenceLabels[field] ?? 'Case information' : 'Case information'
  }

  return evidenceSourceLabels[source] ?? 'Case evidence'
}

function getEvidenceDisplayDetail(source: string, detail: string): string {
  if (source === 'decision_agent' && detail.startsWith('Incomplete evidence from:')) {
    return 'Some essential support information is missing or unavailable.'
  }

  return detail
}

function getEvidenceDisplayValue(value: Evidence['value']): string {
  if (typeof value === 'string' && value.startsWith('EngagementStatus.')) {
    return value.replace('EngagementStatus.', '').toLowerCase()
      .replace(/^./, (letter) => letter.toUpperCase())
  }

  return String(value)
}

function App() {
  const [caseData, setCaseData] = useState<CaseInput>(initialCase)
  const [result, setResult] = useState<WorkflowResult | null>(null)
  const [audit, setAudit] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [auditLoading, setAuditLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeSection, setActiveSection] = useState('case-prioritization')
  const [showTechnicalReview, setShowTechnicalReview] = useState(false)

  useEffect(() => {
    const target = showTechnicalReview
      ? document.getElementById(activeSection)
        ?? document.getElementById('technical-workspace')
      : activeSection === 'case-prioritization'
        ? document.getElementById('case-prioritization')
        : null

    target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [showTechnicalReview, activeSection])

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
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/workflows/run`, {
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
        `${import.meta.env.VITE_API_BASE_URL || ''}/api/audit/${encodeURIComponent(result.audit_reference)}`,
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

  function navigateTo(sectionId: string) {
    if (sectionId === 'agent-workflow' || sectionId === 'audit-evidence') {
      setActiveSection(sectionId)
      setShowTechnicalReview(true)
      return
    }
    setShowTechnicalReview(false)
    setActiveSection(sectionId)
    document.getElementById(sectionId)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }

  const recommendation = result?.final_recommendation
  const actionClass = recommendation?.action.toLowerCase().replaceAll('_', '-')

  const suggestedNextStep = (() => {
    switch (recommendation?.action) {
      case 'PRIORITY_OUTREACH':
        return 'A support coordinator should review the evidence and consider timely student outreach.'
      case 'TUTOR_REVIEW':
        return 'Refer the case to the appropriate tutor for human review of the available indicators.'
      case 'REQUEST_MORE_INFO':
        return 'Confirm the missing case information before deciding on an appropriate support follow-up.'
      case 'NORMAL_FOLLOWUP':
        return 'Continue routine monitoring through the usual academic support process.'
      default:
        return 'Review the available case evidence before selecting a support follow-up.'
    }
  })()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <strong>AA004</strong>
            <span>Student Support Workspace</span>
          </div>
        </div>

        <div className="side-label">WORKSPACE</div>
        <button
          className={`nav-item ${activeSection === 'case-prioritization' ? 'active' : ''}`}
          type="button"
          onClick={() => navigateTo('case-prioritization')}
          aria-current={activeSection === 'case-prioritization' ? 'location' : undefined}
        >
          <span>▦</span> Student Support
        </button>
        <button
          className={`nav-item ${activeSection === 'agent-workflow' ? 'active' : ''}`}
          type="button"
          onClick={() => navigateTo('agent-workflow')}
          aria-current={activeSection === 'agent-workflow' ? 'location' : undefined}
        >
          <span>◎</span> Explainability & Audit
        </button>
        <button
          className={`nav-item ${activeSection === 'audit-evidence' ? 'active' : ''}`}
          type="button"
          onClick={() => navigateTo('audit-evidence')}
          aria-current={activeSection === 'audit-evidence' ? 'location' : undefined}
        >
          <span>◷</span> Audit record
        </button>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>Human-led support review</strong>
            <span>Evidence-based decision support</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">EDUCATION OPERATIONS / AA004</div>
            <h1>Student Support Workspace</h1>
            <p>Review student support indicators and coordinate appropriate follow-up.</p>
          </div>
          <div className="top-status">
            <span className="status-dot" /> Live workflow API
          </div>
        </header>

        <section className="overview-grid">
          <div className="overview-card">
            <span className="metric-label">SUPPORT PROCESS</span>
            <strong>Evidence-led review</strong>
            <small>Review case indicators before choosing a follow-up</small>
          </div>
          <div className="overview-card">
            <span className="metric-label">REVIEW OUTCOMES</span>
            <strong>4 support pathways</strong>
            <small>Routine · Priority · Tutor review · More information</small>
          </div>
          <div className="overview-card">
            <span className="metric-label">DECISION SUPPORT</span>
            <strong>Human-led</strong>
            <small>Recommendations supported by case evidence</small>
          </div>
        </section>

        <div className="workspace-grid">
          <section className="panel input-panel" id="case-prioritization">
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
                <div className="form-field full-width">
                  <label htmlFor="recent-activity">RECENT ACTIVITY INDICATORS</label>
                  <textarea
                    id="recent-activity"
                    rows={3}
                    value={caseData.recent_activity_indicators.join('\n')}
                    placeholder={'Example:\nAttended support session\nSubmitted coursework'}
                    onChange={(e) =>
                      updateField(
                        'recent_activity_indicators',
                        e.target.value
                          .split(/[\n,]+/)
                          .map((item) => item.trim())
                          .filter(Boolean),
                      )
                    }
                  />
                  <p className="form-note">
                    Optional. Enter one indicator per line or separate indicators with commas.
                    These are included in the case evidence; they do not independently change scoring.
                  </p>
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

                <div className="result-section evidence-section">
                  <h4>Supporting evidence</h4>
                  {recommendation?.evidence?.length ? (
                    <ul className="evidence-list">
                      {recommendation.evidence.map((item, index) => (
                        <li key={`${item.source ?? 'evidence'}-${index}`}>
                          {item.source && <strong>{getEvidenceSourceLabel(item.source, item.detail)}</strong>}
                          {item.detail && <p>{getEvidenceDisplayDetail(item.source ?? '', item.detail)}</p>}
                          {item.value !== undefined && item.value !== null && (
                            <small>Recorded value: {getEvidenceDisplayValue(item.value)}</small>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted">No supporting evidence was returned for this recommendation.</p>
                  )}
                </div>

                <div className="result-section next-step-section">
                  <h4>Suggested next step</h4>
                  <p>{suggestedNextStep}</p>
                  <small>Human review is required before taking action.</small>
                </div></>
            )}
          </section>
        </div>


        {error && <div className="error-banner">Request error: {error}</div>}
{showTechnicalReview && (
            <section className="technical-workspace" id="technical-workspace" aria-label="Explainability and audit">
              <div className="technical-workspace-heading">
                <span className="section-kicker">ADVANCED REVIEW</span>
                <h2>Explainability & Audit</h2>
                <p>Inspect workflow execution, technical evidence and the audit record.</p>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => {
                    setShowTechnicalReview(false)
                    setActiveSection('case-prioritization')
                  }}
                >
                  Close advanced review
                </button>
              </div>
              {result ? (
              <>

          <section className="panel context-panel">
            <div className="panel-heading">
              <div>
                <span className="section-kicker">WORKFLOW STATE / CONTEXT</span>
                <h2>Run-scoped shared workflow context</h2>
                <p>
                  Structured state for this workflow execution only. It is not
                  permanent or long-term memory.
                </p>
              </div>
              <span className="count-tag">CURRENT RUN</span>
            </div>

            <div className="context-grid">
              <div className="context-card">
                <h3>Business input</h3>
                <p className="muted">Original case submitted to the workflow.</p>
                <pre className="context-json">
                  {JSON.stringify(result.student_case, null, 2)}
                </pre>
              </div>

              <div className="context-card">
                <h3>Validated case</h3>
                <p className="muted">Normalized output from the Case Intake Agent.</p>
                {result.validated_case ? (
                  <>
                    <pre className="context-json">
                      {JSON.stringify(result.validated_case, null, 2)}
                    </pre>
                    <p>
                      Missing fields:{" "}
                      <strong>
                        {result.validated_case.missing_fields.length
                          ? result.validated_case.missing_fields.join(", ")
                          : "None"}
                      </strong>
                    </p>
                  </>
                ) : (
                  <p className="muted">No validated case was returned.</p>
                )}
              </div>

              <div className="context-card">
                <h3>Domain flags</h3>
                <dl className="context-values">
                  <div>
                    <dt>Attendance flag</dt>
                    <dd>{result.attendance_flag ?? "Not available"}</dd>
                  </div>
                  <div>
                    <dt>Engagement flag</dt>
                    <dd>{result.engagement_flag ?? "Not available"}</dd>
                  </div>
                  <div>
                    <dt>Support load flag</dt>
                    <dd>{result.support_load_flag ?? "Not available"}</dd>
                  </div>
                </dl>
              </div>

              <div className="context-card">
                <h3>Workflow scores</h3>
                {Object.keys(result.scores ?? {}).length ? (
                  <dl className="context-values">
                    {Object.entries(result.scores).map(([name, score]) => (
                      <div key={name}>
                        <dt>{name.replaceAll("_", " ")}</dt>
                        <dd>{score}</dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p className="muted">No scores returned.</p>
                )}
              </div>
            </div>

            <div className="context-meta">
              <span>Workflow ID: <strong>{result.workflow_id}</strong></span>
              <span>
                Created:{" "}
                <strong>
                  {result.created_at
                    ? new Date(result.created_at).toLocaleString()
                    : "Not available"}
                </strong>
              </span>
            </div>
            <div className="context-card">
              <h3>Triggered rule identifiers</h3>
              <div className="tag-list">
                {recommendation?.triggered_rules?.length
                  ? recommendation.triggered_rules.map((rule) => (
                      <span className="rule-tag" key={rule}>{rule}</span>
                    ))
                  : <span className="muted">No rule identifiers returned.</span>}
              </div>
            </div>
          </section>
          <section className="panel agents-panel" id="agent-workflow">
              <div className="panel-heading">
                <div>
                  <span className="section-kicker">03 / EXECUTION TRACE</span>
                  <h2>Agent workflow</h2>
                  <p>Conditional LangGraph execution trace and actual agent outputs returned by the backend.</p>
                </div>
                <span className="count-tag">{result.agent_outputs.length} agents</span>
              </div>

              <div className="graph-trace">
                <div className="graph-trace-heading">
                  <strong>LangGraph conditional execution</strong>
                  <span>{result.node_trace?.length ?? 0} / 8 execution steps completed</span>
                </div>
                {result.node_trace?.length ? (
                  <ol className="graph-node-list">
                    {result.node_trace.map((node, index) => (
                      <li key={`${node}-${index}`}>
                        <span className="graph-node-number">
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        <strong>{node}</strong>
                        <span className="graph-node-status">Completed</span>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="muted">No LangGraph node trace was returned.</p>
                )}
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
                      <div className="agent-responsibility">
                        <strong>Responsibility</strong>
                        <p>
                          {agentDescriptions[agent.agent_name] ??
                            "Processes its assigned workflow responsibility."}
                        </p>
                      </div>
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

                      <h4>Structured agent output</h4>
                      {agent.output_data &&
                      Object.keys(agent.output_data).length > 0 ? (
                        <pre className="agent-output-json">
                          {JSON.stringify(agent.output_data, null, 2)}
                        </pre>
                      ) : (
                        <p className="muted">No structured output data returned.</p>
                      )}
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
                {result.llm_metadata && (
                  <div className="llm-status">
                    <strong>Controlled LLM explanation</strong>
                    <p>
                      Provider: {result.llm_metadata.provider} ·
                      Model: {result.llm_metadata.model}
                    </p>
                    <p>
                      Status: {result.llm_metadata.status} ·
                      Validation: {result.llm_metadata.validation_status}
                    </p>
                    <p>
                      {result.llm_metadata.fallback_used
                        ? 'Deterministic fallback used'
                        : 'Gemini explanation used'}
                    </p>
                  </div>
                )}
              </div>

              <div className="panel audit-panel" id="audit-evidence">
                <span className="section-kicker">05 / AUDITABILITY</span>
                <h2>Audit record</h2>
                <p className="audit-reference">{result.audit_reference}</p>
                <p className="audit-storage-note">
                  MVP storage: audit records are held in backend memory and
                  are not retained after a backend restart.
                </p>
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
              <span className="workflow-error-count">
                {result.errors.length === 0
                  ? 'No workflow errors'
                  : `${result.errors.length} workflow errors`}
              </span>
            </footer>
              </>
            ) : (
              <section className="panel agents-panel">
                <span className="section-kicker">ADVANCED REVIEW</span>
                <h2>Technical details are not available yet</h2>
                <p>
                  Run a case in the Student Support workspace to generate
                  its execution trace and audit evidence.
                </p>
              </section>
            )}
          </section>
        )}<footer className="page-footer">
          AA004 · Student Support Case Prioritization · Evidence-led support workspace
        </footer>
      </main>
    </div>
  )
}

export default App
