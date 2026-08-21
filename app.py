import streamlit as st
import json
from pypdf import PdfReader
from backend.extractor import extract_information
from backend.matcher import suggest_job_roles, match_candidate_to_jd

st.set_page_config(
    page_title="SkillLens — Conversational AI Recruitment Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme & chat interface
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');

  html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', 'Inter', sans-serif;
    background: #0a0d14 !important;
    color: #e2e8f0;
  }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1.5rem 2.5rem 3rem 2.5rem !important; max-width: 1400px !important; }
  h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }

  /* ── Topbar ── */
  .topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 1.5rem 0;
    border-bottom: 1px solid #1e2433;
    margin-bottom: 1.5rem;
  }
  .topbar-logo {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: #f1f5f9;
  }
  .topbar-logo span { color: #6366f1; }
  .topbar-tag {
    background: rgba(99,102,241,0.12);
    color: #818cf8;
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  /* ── Sidebar profile card ── */
  .profile-card {
    background: #0d1117;
    border: 1px solid #1e2433;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
  }
  .profile-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #818cf8;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  /* ── Tags ── */
  .tags-wrap { display: flex; flex-wrap: wrap; gap: 6px; }
  .tag {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 500;
  }
  .tag-skill   { background: rgba(129,140,248,0.12); color: #a5b4fc; border: 1px solid rgba(129,140,248,0.25); }
  .tag-tech    { background: rgba(56,189,248,0.12);  color: #7dd3fc; border: 1px solid rgba(56,189,248,0.25); }
  .tag-lang    { background: rgba(74,222,128,0.1);  color: #86efac; border: 1px solid rgba(74,222,128,0.22); }
  .tag-missing { background: rgba(244,63,94,0.12);  color: #fda4af; border: 1px solid rgba(244,63,94,0.25); }
  .tag-none    { color: #475569; font-size: 0.8rem; font-style: italic; }

  /* ── Role Card ── */
  .role-card {
    background: #0f1422;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
  }
  .role-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
  }
  .role-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1rem; color: #f8fafc; }
  .role-badge { padding: 3px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; }
  .badge-strong { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
  .badge-moderate { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
  .badge-potential { background: rgba(56,189,248,0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); }
  .badge-low { background: rgba(148,163,184,0.1); color: #64748b; border: 1px solid rgba(148,163,184,0.2); }
  .role-desc { font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.6rem; }
  .role-subhead { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 0.3rem; }

  /* ── Match Metric Box ── */
  .match-box {
    background: #0f1422;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 1.2rem;
  }
  .match-score {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #6366f1;
    line-height: 1;
  }

  /* ── Chat Uploader styling ── */
  [data-testid="stFileUploader"] {
    background: #0d1117 !important;
    border: 1px dashed #2d3a52 !important;
    border-radius: 10px !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> tuple[str, int]:
    reader = PdfReader(uploaded_file)
    pages = reader.pages
    text = "\n".join(page.extract_text() or "" for page in pages)
    return text.strip(), len(pages)

def update_candidate_profile(extracted_entities: dict):
    """Accumulates candidate entities into session state."""
    for category in ["skills", "technologies", "languages"]:
        existing = set(st.session_state.candidate_entities.get(category, []))
        new_items = extracted_entities.get(category, [])
        for item in new_items:
            existing.add(item)
        st.session_state.candidate_entities[category] = list(existing)

def get_total_entity_count(entities: dict) -> int:
    return sum(len(entities.get(k, [])) for k in ["skills", "technologies", "languages"])


def format_role_suggestions_html(suggestions: list) -> str:
    html = "<div><div style='font-weight: 600; font-size: 0.9rem; color: #cbd5e1; margin-bottom: 0.6rem;'>Ranked Job Role Matches:</div>"
    for sug in suggestions[:5]:
        suit = sug["suitability"]
        badge_cls = "badge-strong" if suit == "Strong Fit" else "badge-moderate" if suit == "Moderate Fit" else "badge-potential" if suit == "Potential Fit" else "badge-low"
        matched_tags = "".join(f'<span class="tag tag-skill">{s}</span>' for s in sug["matched_skills"]) if sug["matched_skills"] else '<span class="tag-none">None</span>'
        missing_req = "".join(f'<span class="tag tag-missing">{s}</span>' for s in sug["missing_required"]) if sug["missing_required"] else '<span class="tag-none">None</span>'

        html += f'<div class="role-card"><div class="role-card-header"><div class="role-title">{sug["role"]} &bull; {sug["match_score"]}% Match</div><div class="role-badge {badge_cls}">{suit}</div></div><div class="role-desc">{sug["description"]}</div><div style="margin-bottom: 0.4rem;"><div class="role-subhead">Matched Skills</div><div class="tags-wrap">{matched_tags}</div></div><div><div class="role-subhead">Missing Skill Gap</div><div class="tags-wrap">{missing_req}</div></div></div>'
    html += "</div>"
    return html

def format_jd_match_html(match_res: dict) -> str:
    matched_tags = "".join(f'<span class="tag tag-skill">{s}</span>' for s in match_res["matched_skills"]) if match_res["matched_skills"] else '<span class="tag-none">No skill overlap</span>'
    missing_tags = "".join(f'<span class="tag tag-missing">{s}</span>' for s in match_res["missing_skills"]) if match_res["missing_skills"] else '<span class="tag-none">Zero Gap! Meets 100% of skills</span>'

    return f'<div class="match-box"><div class="match-score">{match_res["match_score"]}%</div><div><div style="font-family: Space Grotesk; font-size: 1.1rem; font-weight: 700; color: #f1f5f9;">{match_res["suitability"]}</div><div style="color: #64748b; font-size: 0.8rem; margin-top: 2px;">Matched {len(match_res["matched_skills"])} out of {len(match_res["jd_skills"])} skills required in the Job Description.</div></div></div><div style="margin-bottom: 0.6rem;"><div class="role-subhead">Matched Overlapping Skills</div><div class="tags-wrap">{matched_tags}</div></div><div><div class="role-subhead">Missing JD Skills Gap</div><div class="tags-wrap">{missing_tags}</div></div>'


# ── Rule-Based Chatbot Dialogue Engine ───────────────────────────────────────
def generate_bot_response(user_text: str) -> tuple[str, str]:
    """
    Local Rule-Based Bot Engine.
    Identifies user intent, runs NLP extraction, updates profile, or runs JD matching.
    Returns (bot_response_markdown, response_type).
    """
    text_lower = user_text.lower().strip()

    # Intent 1: User explicitly asks for job suggestions
    if any(k in text_lower for k in ["suggest job", "suggest role", "what job", "suitable job", "role suggestion", "my roles"]):
        total_ent = get_total_entity_count(st.session_state.candidate_entities)
        if total_ent == 0:
            return (
                "I haven't extracted any skills from your profile yet! Please tell me about your background, experience, or tools (e.g. *'I have 3 years of experience in Python, PyTorch, and NLP'*) or upload your resume above.",
                "text"
            )
        suggestions = suggest_job_roles(st.session_state.candidate_entities)
        top_role = suggestions[0]["role"]
        reply_html = f"<div style='margin-bottom: 0.8rem;'>Based on your extracted skills profile (<strong>{total_ent} entities</strong> detected), here are your top recommended job roles. Your best fit is <strong>{top_role}</strong> ({suggestions[0]['match_score']}% match):</div>"
        reply_html += format_role_suggestions_html(suggestions)
        return (reply_html, "html")

    # Intent 2: User provides a Job Description to match against
    if any(k in text_lower for k in ["job description", "match jd", "match job", "requirements:", "looking for", "responsibilities:"]) or len(user_text.split()) > 35:
        # Check if candidate has skills extracted first
        total_ent = get_total_entity_count(st.session_state.candidate_entities)

        # Extract entities from this input to check if it looks like a JD
        jd_extracted = extract_information(user_text)
        jd_entities_count = get_total_entity_count(jd_extracted)

        # If user input contains JD keywords or looks like JD format
        if "looking for" in text_lower or "requirements" in text_lower or "job description" in text_lower or (jd_entities_count >= 2 and total_ent > 0):
            if total_ent == 0:
                # If candidate hasn't provided resume/bio yet, treat this text as candidate text instead, or prompt
                update_candidate_profile(jd_extracted)
                suggestions = suggest_job_roles(st.session_state.candidate_entities)
                reply_html = f"<div style='margin-bottom: 0.8rem;'>I've extracted <strong>{jd_entities_count} entities</strong> from your statement and created your profile! Here are your auto-suggested roles:</div>"
                reply_html += format_role_suggestions_html(suggestions)
                return (reply_html, "html")
            else:
                # Run JD matching against accumulated candidate profile
                match_res = match_candidate_to_jd(st.session_state.candidate_entities, user_text, jd_extracted)
                reply_html = f"<h4 style='font-family: Space Grotesk; margin-bottom: 0.4rem; color: #f1f5f9;'>Job Description Match Analysis</h4><div style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 0.8rem;'>Matched your candidate profile against the provided Job Description:</div>"
                reply_html += format_jd_match_html(match_res)
                return (reply_html, "html")

    # Intent 3: Greeting / Help
    if text_lower in ["hi", "hello", "hey", "help", "start"]:
        return (
            "Hello! I am your AI Recruitment & Skill Assistant. You can:\n"
            "1. **Tell me about your experience** or paste your bio (e.g. *'I built NLP models in Python using spaCy and PyTorch'*).\n"
            "2. **Upload a PDF resume** using the uploader above.\n"
            "3. Ask me to **'suggest job roles'** based on your extracted skills.\n"
            "4. Paste a **Job Description** to get an automated candidate match score & skill gap analysis!",
            "text"
        )

    # Default Intent: Extract skills/tech/languages from user input & update candidate profile
    extracted = extract_information(user_text)
    num_found = get_total_entity_count(extracted)

    if num_found > 0:
        update_candidate_profile(extracted)
        total_accumulated = get_total_entity_count(st.session_state.candidate_entities)

        all_found = extracted.get("skills", []) + extracted.get("technologies", []) + extracted.get("languages", [])
        found_str = ", ".join(f"**{item}**" for item in all_found)

        suggestions = suggest_job_roles(st.session_state.candidate_entities)
        top_sug = suggestions[0]

        reply_md = f"I extracted **{num_found} entity/entities** from your input: {found_str}.\n\n"
        reply_md += f"Your cumulative profile now has **{total_accumulated} skills & tools**.\n\n"
        reply_md += f"💡 **Top Suggested Role:** **{top_sug['role']}** ({top_sug['match_score']}% match - {top_sug['suitability']})\n\n"
        reply_md += "*Type **'suggest job roles'** to view full role breakdown or paste a **Job Description** to test matching.*"
        return (reply_md, "text")

    else:
        return (
            "I couldn't detect any specific skills or technologies in your text. "
            "Try mentioning programming languages (Python, SQL), frameworks (React, PyTorch), or domains (Machine Learning, DevOps), or upload your PDF resume above!",
            "text"
        )


# ── Initialize Session State ──────────────────────────────────────────────────
if "candidate_entities" not in st.session_state:
    st.session_state.candidate_entities = {"skills": [], "technologies": [], "languages": []}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am **SkillLens AI**, your rule-based recruitment chatbot.\n\n"
                       "Share your technical background, upload a **PDF resume**, or paste a **Job Description** to get automated skill extraction, role recommendations, and candidate matching!",
            "type": "text"
        }
    ]


# ── App Layout ────────────────────────────────────────────────────────────────

# Topbar
st.markdown("""
<div class="topbar">
  <div class="topbar-logo">Skill<span>Lens</span> AI Bot</div>
  <div class="topbar-tag">No LLM API &mdash; Local Rule-Based Chatbot</div>
</div>
""", unsafe_allow_html=True)

# Main Grid: Left Column (Live Candidate Profile) | Right Column (Chatbot)
col_left, col_right = st.columns([1, 2.2], gap="large")


# ════════════════════════════════════════════════════════
# LEFT COLUMN — Live Extracted Candidate Profile
# ════════════════════════════════════════════════════════
with col_left:
    st.markdown("### 📄 Candidate Skill Profile")

    # Resume Upload Box inside Sidebar/Left Panel
    uploaded_pdf = st.file_uploader(
        "Upload PDF Resume",
        type=["pdf"],
        key="chat_pdf_uploader",
        help="Upload PDF resume to automatically parse skills into this conversation."
    )

    if uploaded_pdf is not None:
        if "last_uploaded_filename" not in st.session_state or st.session_state.last_uploaded_filename != uploaded_pdf.name:
            st.session_state.last_uploaded_filename = uploaded_pdf.name
            with st.spinner("Extracting text from PDF resume..."):
                pdf_text, p_count = extract_pdf_text(uploaded_pdf)
                if pdf_text:
                    pdf_entities = extract_information(pdf_text)
                    update_candidate_profile(pdf_entities)
                    ent_count = get_total_entity_count(pdf_entities)

                    # Add user & bot messages to chat
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"📎 Uploaded resume: **{uploaded_pdf.name}** ({p_count} pages)",
                        "type": "text"
                    })

                    suggestions = suggest_job_roles(st.session_state.candidate_entities)
                    bot_msg = f"<div style='margin-bottom: 0.6rem;'>Successfully parsed <strong>{uploaded_pdf.name}</strong>! Extracted <strong>{ent_count} entities</strong> (skills, technologies, languages).</div>"
                    bot_msg += f"<div style='color: #818cf8; font-weight: 600; margin-bottom: 0.8rem;'>Top Suggested Role: {suggestions[0]['role']} ({suggestions[0]['match_score']}% match)</div>"
                    bot_msg += format_role_suggestions_html(suggestions)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_msg,
                        "type": "html"
                    })

    # Render Profile Cards
    cand = st.session_state.candidate_entities
    tot_entities = get_total_entity_count(cand)

    st.markdown(f"""
    <div style="background: #0d1117; border: 1px solid #1e2433; border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
      <span style="font-family: 'Space Grotesk'; font-weight: 700; color: #f1f5f9;">Total Entities Extracted</span>
      <span style="font-family: 'Space Grotesk'; font-size: 1.3rem; font-weight: 700; color: #6366f1;">{tot_entities}</span>
    </div>
    """, unsafe_allow_html=True)

    categories = [
        ("Skills", cand.get("skills", []), "tag-skill"),
        ("Technologies", cand.get("technologies", []), "tag-tech"),
        ("Programming Languages", cand.get("languages", []), "tag-lang"),
    ]

    for cat_title, items, tag_cls in categories:
        tags_html = (
            "".join(f'<span class="tag {tag_cls}">{item}</span>' for item in items)
            if items else '<span class="tag-none">None detected yet.</span>'
        )
        st.markdown(f"""
        <div class="profile-card">
          <div class="profile-header">
            <span>{cat_title}</span>
            <span style="color: #64748b; font-size: 0.75rem;">{len(items)}</span>
          </div>
          <div class="tags-wrap">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Reset Profile & Chat", use_container_width=True):
        st.session_state.candidate_entities = {"skills": [], "technologies": [], "languages": []}
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Profile reset! Tell me about your background or upload a resume to start fresh.",
                "type": "text"
            }
        ]
        st.rerun()


# ════════════════════════════════════════════════════════
# RIGHT COLUMN — Interactive Recruitment Chatbot Interface
# ════════════════════════════════════════════════════════
with col_right:
    st.markdown("### 💬 Recruitment Chat Assistant")

    # Display chat message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "html":
                st.markdown(msg["content"], unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

    # Chat Input box
    if prompt := st.chat_input("Type your response, skills, 'suggest job roles', or paste a Job Description..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})

        # Generate response using Rule-Based Engine
        bot_reply, reply_type = generate_bot_response(prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_reply,
            "type": reply_type
        })
        st.rerun()