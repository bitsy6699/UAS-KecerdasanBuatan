import { useState, useRef, useEffect, useCallback } from 'react'
import BlinkingAsciiDots from './BlinkingAsciiDots'

const API = '/api'

type Role = 'user' | 'assistant'
type Message = { role: Role; content: string }

type TemplateMap = Record<string, { label: string; desc: string }>

const TEMPLATES: TemplateMap = {
  master: { label: 'Formal Akademis', desc: 'PRD formal untuk tugas kuliah, TA, atau proyek akademik' },
  startup: { label: 'Startup / MVP', desc: 'Ringkas, fokus ke hipotesis, validasi cepat' },
  mobile: { label: 'Mobile App', desc: 'Spesifik untuk aplikasi mobile' },
  enterprise: { label: 'Enterprise / Fitur Internal', desc: 'Untuk fitur di sistem enterprise' },
  data: { label: 'Data & Analytics', desc: 'Produk data — pipeline, metrik, dashboard' },
}

function Logo({ maxW = '140px' }: { maxW?: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <img src="/assets.png" alt="logo" style={{ maxWidth: maxW, height: 'auto', imageRendering: 'pixelated' }} />
    </div>
  )
}

function DotLoader() {
  return (
    <span>
      <span className="pixel-dot">.</span>
      <span className="pixel-dot">.</span>
      <span className="pixel-dot">.</span>
    </span>
  )
}

function useTheme() {
  const [theme, setTheme] = useState<'dark' | 'light'>(
    window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  )
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => setTheme(e.matches ? 'dark' : 'light')
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])
  return theme
}

function useTemplates() {
  const [templates, setTemplates] = useState<TemplateMap>(TEMPLATES)
  useEffect(() => {
    fetch(`${API}/templates`)
      .then(r => r.json())
      .then(data => setTemplates(data))
      .catch(() => {})
  }, [])
  return templates
}

function useServerStatus() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  useEffect(() => {
    let cancelled = false
    const check = () => {
      fetch(`${API}/templates`)
        .then(() => { if (!cancelled) setStatus('online') })
        .catch(() => { if (!cancelled) setStatus('offline') })
    }
    check()
    const id = setInterval(check, 5000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])
  return status
}

export default function App() {
  useTheme()
  const templates = useTemplates()
  const serverStatus = useServerStatus()
  const templateKeys = Object.keys(templates)

  const [messages, setMessages] = useState<Message[]>([])
  const [generating, setGenerating] = useState(false)
  const [templateKey, setTemplateKey] = useState('startup')
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [partial, setPartial] = useState('')
  const [modelStatus, setModelStatus] = useState('Memuat model...')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const bgColor = '#1a1a1a'
  const dotColor = '220, 38, 38'
  const chatEnd = useRef<HTMLDivElement>(null)
  const abortRef = useRef(false)

  const scrollDown = useCallback(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => { scrollDown() }, [messages, partial, scrollDown])

  useEffect(() => {
    if (!generating || !sessionId) return
    const es = new EventSource(`${API}/chat/${sessionId}/stream`)
    let full = ''

    es.addEventListener('message', (e) => {
      full += e.data
      setPartial(full)
      scrollDown()
    })

    es.addEventListener('error', (e) => {
      const err = (e as MessageEvent).data || 'Generation error'
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err}` }])
      setPartial('')
      setGenerating(false)
      setSessionId(null)
      es.close()
    })

    es.addEventListener('done', () => {
      if (full) {
        setMessages(prev => [...prev, { role: 'assistant', content: full }])
      }
      setPartial('')
      setGenerating(false)
      setSessionId(null)
      es.close()
    })

    es.onerror = () => {
      if (abortRef.current) return
      if (full) {
        setMessages(prev => [...prev, { role: 'assistant', content: full }])
      }
      setPartial('')
      setGenerating(false)
      setSessionId(null)
      es.close()
    }

    return () => { es.close() }
  }, [generating, sessionId, scrollDown])

  useEffect(() => {
    if (generating) {
      setModelStatus('Menulis...')
    } else {
      setModelStatus('Model aktif')
    }
  }, [generating])

  const handleSend = useCallback(async () => {
    if (!input.trim() || generating) return

    const userMsg: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setGenerating(true)
    setPartial('')
    abortRef.current = false

    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: input,
        }),
      })
      const data = await res.json()
      setSessionId(data.session_id)
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Gagal terhubung ke server' }])
      setGenerating(false)
    }
  }, [input, generating, templateKey])

  const handleStop = useCallback(async () => {
    abortRef.current = true
    if (sessionId) {
      await fetch(`${API}/chat/${sessionId}/stop`, { method: 'POST' })
    }
    if (partial) {
      setMessages(prev => [...prev, { role: 'assistant', content: partial }])
    }
    setPartial('')
    setGenerating(false)
    setSessionId(null)
  }, [sessionId, partial])

  const handleClear = useCallback(() => {
    setMessages([])
    setPartial('')
    setGenerating(false)
    setSessionId(null)
  }, [])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const downloadMarkdown = (content: string, _i: number) => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'prd_generated.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app-layout">
      <aside className={`sidebar ${sidebarOpen ? '' : 'closed'}`}>
        <div className="sidebar-content">
          <Logo maxW="80px" />
          <div className="brand">
            loehoer<span className="red">.</span>ai
            <br />
            <span className="brand-sub">PRD Generator</span>
          </div>
          <hr />
          <p className="sidebar-desc">
            AI yang menyusun PRD terstruktur dari ide fitur atau produk kamu.
          </p>

          <div className="model-status">{modelStatus}</div>

          {serverStatus === 'offline' && (
            <div className="server-offline">⚠ server offline — jalankan backend</div>
          )}

          <hr />

          <button className="btn" onClick={handleClear} style={{ width: '100%' }}>
            [ hapus ]
          </button>

          <hr />

          <label className="label">Template</label>
          <div className="template-list">
            {templateKeys.map(k => (
              <button
                key={k}
                className={`template-btn ${templateKey === k ? 'active' : ''}`}
                onClick={() => setTemplateKey(k)}
              >
                {templates[k]?.label ?? k}
              </button>
            ))}
          </div>
          <p className="template-desc">
            {templates[templateKey]?.desc ?? ''}
          </p>

          <hr />
          <p className="version">v2.2 &nbsp; Groq cloud 8B</p>
        </div>
      </aside>
      <div className="app-bg">
        <BlinkingAsciiDots
          backgroundColor={bgColor}
          textColor={dotColor}
          density={1.5}
          animationSpeed={0.5}
        />
      </div>
      <button className={`sidebar-toggle ${sidebarOpen ? '' : 'closed'}`} onClick={() => setSidebarOpen(o => !o)}>
        {sidebarOpen ? '◀' : '▶'}
      </button>
      <main className="main">
        <div className="chat-header">
          <Logo maxW="clamp(90px, 18vw, 140px)" />
          <div className="header-text">
            <span className="title">
              loehoer<span className="red">.</span>ai
            </span>
            <span className="badge">prd</span>
            <br />
            <span className="subtitle">
              Masukkan kebutuhan fitur atau produk, AI akan menyusun PRD terstruktur.
            </span>
          </div>
          <hr />
        </div>

        {serverStatus === 'offline' && (
          <div className="alert-error">
            ⚠ Tidak dapat terhubung ke server backend. Pastikan server sudah jalan:
            <br />
            <code>python3 backend/main.py</code> (dari folder UAS-KecerdasanBuatan)
          </div>
        )}

        {messages.length === 0 && !generating && (
          <div className="welcome-msg">
            <strong>loehoer.ai</strong> — PRD Generator&emsp;`v2.2`
            <br /><br />
            Ketik kebutuhan fitur atau produk kamu, AI akan menyusun PRD terstruktur per bagian.
            <br /><br />
            `├ apa itu ...` → AI menjelaskan konsep<br />
            `└ buatkan ...` &nbsp;→ AI menghasilkan PRD
          </div>
        )}

        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`msg msg-${msg.role}`}>
              <div className="msg-bubble">
                <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                {msg.role === 'assistant' && msg.content.length > 100 && !msg.content.startsWith('Error') && (
                  <button className="btn btn-small" onClick={() => downloadMarkdown(msg.content, i)}>
                    [ download .md ]
                  </button>
                )}
              </div>
            </div>
          ))}
          {generating && partial && (
            <div className="msg msg-assistant">
              <div className="msg-bubble">
                <div dangerouslySetInnerHTML={{ __html: renderMarkdown(partial) }} />
                <span className="pixel-cursor">&#x2588;</span>
              </div>
            </div>
          )}
          <div ref={chatEnd} />
        </div>

        {generating && (
          <div className="stop-bar">
            <span className="stop-text">menulis<DotLoader /></span>
            <button className="btn btn-stop" onClick={handleStop}>■ stop</button>
          </div>
        )}

        <div className="input-area">
          <input
            className="chat-input"
            placeholder="Masukkan Prompt..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={generating}
          />
        </div>
      </main>
    </div>
  )
}

function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  const lines = html.split('\n')
  let out = ''
  let inList = false

  for (const line of lines) {
    const hd = line.match(/^(#{1,3})\s+(.+)/)
    if (hd) {
      if (inList) { out += '</ul>'; inList = false }
      const level = hd[1].length
      out += `<h${level}>${hd[2]}</h${level}>\n`
      continue
    }
    const li = line.match(/^[-*]\s+(.+)/)
    if (li) {
      if (!inList) { out += '<ul>'; inList = true }
      out += `<li>${inlineFormat(li[1])}</li>\n`
      continue
    }
    if (inList) { out += '</ul>'; inList = false }
    if (line.trim() === '') {
      out += '\n'
    } else {
      out += `<p>${inlineFormat(line)}</p>\n`
    }
  }
  if (inList) out += '</ul>'

  return out
}

function inlineFormat(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}
