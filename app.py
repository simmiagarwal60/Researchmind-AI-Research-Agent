import streamlit as st
import time
from agents import build_scrape_agent, build_search_agent, writer_chain, critic_chain
from langchain.agents import create_agent
import httpx

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #070b14;
    --surface: #0d1320;
    --surface-2: #111a2a;
    --border: rgba(148,163,184,.14);
    --text: #f8fafc;
    --muted: #94a3b8;
    --purple: #8b5cf6;
    --cyan: #22d3ee;
    --green: #34d399;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(139,92,246,.16), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(34,211,238,.10), transparent 28%),
        linear-gradient(180deg, #070b14 0%, #09101d 55%, #070b14 100%);
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1.5rem 3rem 4rem;
    max-width: 1380px;
}

/* Top navigation */
.topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding: .8rem 1.1rem;
    margin-bottom: 2.5rem;
    border: 1px solid var(--border);
    background: rgba(13,19,32,.72);
    backdrop-filter: blur(18px);
    border-radius: 16px;
    box-shadow: 0 12px 40px rgba(0,0,0,.22);
}
.brand {
    display:flex;
    align-items:center;
    gap:.75rem;
    font-family:'Space Grotesk',sans-serif;
    font-weight:700;
    font-size:1rem;
}
.brand-icon {
    width:34px;height:34px;
    display:grid;place-items:center;
    border-radius:10px;
    background:linear-gradient(135deg,var(--purple),var(--cyan));
    box-shadow:0 0 24px rgba(139,92,246,.28);
}
.top-status {
    font-size:.72rem;
    color:#a7f3d0;
    border:1px solid rgba(52,211,153,.18);
    background:rgba(52,211,153,.07);
    padding:.4rem .7rem;
    border-radius:999px;
}

/* Hero */
.hero {
    text-align:left;
    padding: .5rem 0 2.2rem;
}
.hero-eyebrow {
    display:inline-flex;
    align-items:center;
    gap:.45rem;
    font-size:.68rem;
    font-weight:700;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:#a78bfa;
    background:rgba(139,92,246,.09);
    border:1px solid rgba(139,92,246,.18);
    border-radius:999px;
    padding:.42rem .72rem;
    margin-bottom:1rem;
}
.hero h1 {
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(2.7rem,5.5vw,5rem);
    font-weight:700;
    line-height:.98;
    letter-spacing:-.045em;
    margin:0 0 1rem;
    color:#f8fafc;
}
.hero h1 span {
    background:linear-gradient(90deg,#a78bfa,#22d3ee);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-sub {
    font-size:1rem;
    color:var(--muted);
    max-width:680px;
    margin:0;
    line-height:1.75;
}
.divider {
    height:1px;
    background:linear-gradient(90deg,rgba(139,92,246,.35),rgba(34,211,238,.08),transparent);
    margin:1.2rem 0 2rem;
}

/* Cards */
.input-card {
    background:linear-gradient(145deg,rgba(17,26,42,.92),rgba(9,15,27,.92));
    border:1px solid rgba(139,92,246,.18);
    border-radius:20px;
    padding:1.7rem;
    margin-bottom:1rem;
    box-shadow:0 18px 55px rgba(0,0,0,.20);
}
.stTextInput > div > div > input {
    background:#080e19 !important;
    border:1px solid rgba(148,163,184,.16) !important;
    border-radius:12px !important;
    color:#f8fafc !important;
    font-size:.95rem !important;
    padding:.82rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color:var(--purple) !important;
    box-shadow:0 0 0 3px rgba(139,92,246,.12) !important;
}
.stTextInput > label {
    color:#c4b5fd !important;
    font-size:.76rem !important;
    font-weight:700 !important;
    letter-spacing:.06em !important;
    text-transform:uppercase !important;
}

.stButton > button {
    background:linear-gradient(135deg,#8b5cf6,#6366f1) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.10) !important;
    border-radius:12px !important;
    padding:.78rem 1rem !important;
    font-family:'Inter',sans-serif !important;
    font-weight:700 !important;
    box-shadow:0 8px 28px rgba(99,102,241,.28) !important;
    transition:all .2s ease !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 12px 34px rgba(139,92,246,.38) !important;
    border-color:rgba(167,139,250,.45) !important;
}

/* Example chips */
.example-wrap {
    display:flex;
    gap:.5rem;
    flex-wrap:wrap;
    align-items:center;
    margin:.7rem 0 1.5rem;
}
.example-label {
    font-size:.67rem;
    color:#64748b;
    font-weight:700;
    letter-spacing:.12em;
}
.example-chip {
    background:rgba(255,255,255,.035);
    border:1px solid rgba(148,163,184,.13);
    border-radius:999px;
    padding:.38rem .72rem;
    font-size:.72rem;
    color:#aebbd0;
}

/* Pipeline */
.section-heading {
    font-family:'Space Grotesk',sans-serif;
    font-size:1.05rem;
    font-weight:700;
    color:#f8fafc;
    margin:0 0 1rem;
}
.pipeline-head {
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:1rem;
}
.pipeline-count {
    font-size:.68rem;
    color:#64748b;
    background:rgba(255,255,255,.04);
    border:1px solid var(--border);
    padding:.3rem .55rem;
    border-radius:999px;
}
.step-card {
    background:rgba(13,19,32,.82);
    border:1px solid rgba(148,163,184,.12);
    border-radius:15px;
    padding:1rem 1.1rem;
    margin-bottom:.7rem;
    position:relative;
    overflow:hidden;
    transition:all .2s ease;
}
.step-card:hover {
    transform:translateX(2px);
    border-color:rgba(139,92,246,.28);
}
.step-card.active {
    border-color:rgba(139,92,246,.48);
    background:linear-gradient(90deg,rgba(139,92,246,.10),rgba(13,19,32,.86));
    box-shadow:0 0 30px rgba(139,92,246,.08);
}
.step-card.done {
    border-color:rgba(52,211,153,.25);
    background:linear-gradient(90deg,rgba(52,211,153,.06),rgba(13,19,32,.86));
}
.step-card::before {
    content:'';
    position:absolute;
    left:0;top:0;bottom:0;width:3px;
    background:rgba(148,163,184,.08);
}
.step-card.active::before { background:linear-gradient(#8b5cf6,#22d3ee); }
.step-card.done::before { background:#34d399; }
.step-header {
    display:flex;
    align-items:center;
    gap:.7rem;
}
.step-num {
    font-family:'Space Grotesk',sans-serif;
    font-size:.7rem;
    font-weight:700;
    color:#8b5cf6;
}
.step-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:.9rem;
    font-weight:700;
    color:#e2e8f0;
}
.step-status {
    margin-left:auto;
    font-size:.62rem;
    font-weight:700;
    letter-spacing:.08em;
}
.status-waiting { color:#475569; }
.status-running { color:#a78bfa; }
.status-done { color:#34d399; }

/* Results */
.result-panel,.report-panel,.feedback-panel {
    background:rgba(13,19,32,.72);
    border:1px solid rgba(148,163,184,.12);
    border-radius:18px;
    padding:1.5rem 1.7rem;
    margin-top:1rem;
    margin-bottom:1rem;
    box-shadow:0 12px 35px rgba(0,0,0,.14);
}
.result-panel-title,.panel-label {
    font-size:.68rem;
    font-weight:700;
    letter-spacing:.12em;
    text-transform:uppercase;
    padding-bottom:.7rem;
    margin-bottom:1rem;
    border-bottom:1px solid rgba(148,163,184,.10);
}
.result-panel-title,.panel-label.orange { color:#a78bfa; }
.panel-label.green { color:#34d399; }
.result-content {
    font-size:.88rem;
    line-height:1.8;
    color:#cbd5e1;
    white-space:pre-wrap;
}
.report-panel {
    border-color:rgba(139,92,246,.20);
}
.feedback-panel {
    border-color:rgba(52,211,153,.18);
}

/* Streamlit markdown and expanders */
.stMarkdown { color:#cbd5e1; }
details {
    background:rgba(255,255,255,.018);
    border:1px solid rgba(148,163,184,.08);
    border-radius:12px;
    padding:.2rem .7rem;
    margin-bottom:.7rem;
}
details summary {
    color:#94a3b8 !important;
    font-size:.74rem !important;
    font-weight:600 !important;
}
.stSpinner > div { color:#a78bfa !important; }

/* Download button */
.stDownloadButton > button {
    background:transparent !important;
    color:#c4b5fd !important;
    border:1px solid rgba(139,92,246,.30) !important;
    border-radius:10px !important;
    font-weight:600 !important;
}
.stDownloadButton > button:hover {
    background:rgba(139,92,246,.08) !important;
    border-color:rgba(139,92,246,.55) !important;
}

/* Footer */
.notice {
    font-size:.68rem;
    color:#475569;
    text-align:center;
    margin-top:3rem;
    padding-top:1.5rem;
    border-top:1px solid rgba(148,163,184,.08);
    letter-spacing:.04em;
}

/* Responsive */
@media (max-width: 900px) {
    .block-container { padding:1rem 1rem 3rem; }
    .topbar { margin-bottom:1.5rem; }
    .hero h1 { font-size:3rem; }
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="brand-icon">✦</div>
        ResearchMind
    </div>
    <div class="top-status">● Multi-agent system online</div>
</div>

<div class="hero">
    <div class="hero-eyebrow">✦ AI Research Workspace</div>
    <h1>Research, <span>without the busywork.</span></h1>
    <p class="hero-sub">
        Give ResearchMind a topic and let specialized agents search the web,
        extract deeper context, write the report, and critically review the result.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div class="example-wrap">
        <span class="example-label">TRY</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background:rgba(255,255,255,.035);
            border:1px solid rgba(148,163,184,.13);
            border-radius:999px;
            padding:.38rem .72rem;
            font-size:.72rem;
            color:#aebbd0;
            font-family:'Inter',sans-serif;
            cursor:default;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown("""
    <div class="pipeline-head">
        <div class="section-heading">Agent Pipeline</div>
        <div class="pipeline-count">4 stages</div>
    </div>
    """, unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        # figure out which steps are done
        if step in r:
            return "done"
        # which step is running now (first not in r)
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("🔍  Search Agent is working…"):
        search_agent = build_search_agent()
        import httpx

    sr = search_agent.invoke({
            "messages": [
                ("user", f"Find recent, reliable and detailed information about: {topic_val}")
            ]
    })
    results["search"] = sr["messages"][-1].content
    st.session_state.results = dict(results)
    st.rerun() if False else None   # keep inline for now

    # ── Step 2: Reader ──
    with st.spinner("📄  Reader Agent is scraping top resources…"):
        reader_agent = build_scrape_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("✍️  Writer is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("🧐  Critic is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)