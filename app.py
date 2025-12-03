import os

from dotenv import load_dotenv
import streamlit as st
from groq import Groq

# ==============================
# Setup – API key & client
# ==============================
# Locally:  .env  →  GROQ_API_KEY=...
# Streamlit Cloud: Settings → Secrets → GROQ_API_KEY="..."
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.warning(
        "⚠️ GROQ_API_KEY is not set.\n\n"
        "• Locally: create a `.env` file with `GROQ_API_KEY=...`\n"
        "• On Streamlit Cloud: add `GROQ_API_KEY` in **Settings → Secrets**."
    )
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="🤖",
    layout="centered",
)

# Global CSS for nicer UI
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1d4ed8 0, #020617 35%, #020617 100%);
        color: #e5e7eb;
    }
    .main-card {
        background: rgba(15,23,42,0.95);
        border-radius: 18px;
        padding: 24px 22px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.5);
        max-width: 800px;
        margin: 32px auto;
        border: 1px solid rgba(148,163,184,0.5);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# Session State
# ==============================
if "view" not in st.session_state:
    st.session_state.view = "intro"   # "intro" -> "chat"

if "stage" not in st.session_state:
    st.session_state.stage = "form"   # "form" -> "questions" -> "ended"

if "history_messages" not in st.session_state:
    st.session_state.history_messages = []   # expander

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []      # live chat under questions

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

if "latest_questions" not in st.session_state:
    st.session_state.latest_questions = ""   # markdown string

if "show_contact" not in st.session_state:
    st.session_state.show_contact = False

END_KEYWORDS = ["bye", "goodbye", "quit", "exit", "stop", "thank you", "thanks"]

# Rough list of common tech keywords to validate tech stack
KNOWN_TECH_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node", "django", "flask", "spring", "flutter", "kotlin", "swift",
    "html", "css", "tailwind", "bootstrap", "sql", "mysql", "postgres",
    "mongodb", "redis", "nlp", "computer vision", "cv", "pytorch",
    "tensorflow", "sklearn", "scikit", "docker", "kubernetes", "aws",
    "azure", "gcp", "linux", "bash", "git"
]

OUT_OF_SCOPE_KEYWORDS = [
    "story", "joke", "poem", "song", "lyrics", "weather",
    "news", "movie", "games", "time pass"
]


def is_end_keyword(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in END_KEYWORDS)


def looks_like_tech_stack(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in KNOWN_TECH_KEYWORDS)


def add_history(role: str, content: str):
    st.session_state.history_messages.append({"role": role, "content": content})


def add_chat(role: str, content: str):
    st.session_state.chat_messages.append({"role": role, "content": content})


# ==============================
# Fallback markdown (if Groq fails)
# ==============================
def _generic_fallback_markdown() -> str:
    """Fallback: generic questions if Groq fails."""
    return """
### General

1. Tell me about a recent project you worked on and what your role was.
2. How do you usually debug and fix tricky issues in your code?
3. How do you keep yourself updated with new tools, frameworks, or libraries?
4. Describe a situation where you had to learn a new technology quickly.

**Mini Assignment:**  
Pick one of your past projects and refactor it to improve code readability and structure.  
Write down what you improved and why.
    """.strip()


# ==============================
# LLM helper – generate questions per tech
# ==============================
def generate_technical_questions_markdown(tech_stack: str) -> str:
    """
    Use Groq LLM to create markdown questions + mini assignments per tech.
    """
    system_prompt = """
You are an experienced technical interviewer for software roles.

The candidate will give you a TECH STACK string (comma-separated or space-separated),
for example: "Python, Flutter, React, PostgreSQL".

Your task:

- Extract the distinct technologies from the string.
- For EACH technology, create a section in this exact format:

### <Technology Name>
1. Question 1 (short, practical, and specific to this technology)
2. Question 2
3. Question 3

**Mini Assignment:** One small hands-on task that uses ONLY this technology.

RULES:
- Every technology MUST have its OWN section.
- Questions MUST be about that technology.
- Respond ONLY in markdown as described. No intro, no summary, no extra text.
""".strip()

    user_prompt = f"Candidate tech stack: {tech_stack}"

    if client is None:
        st.error("⚠️ GROQ_API_KEY is missing or invalid. Using generic questions instead.")
        return _generic_fallback_markdown()

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        content = resp.choices[0].message.content.strip()

        if "###" not in content:
            st.warning("LLM response was not in the expected format. Showing a generic set instead.")
            return _generic_fallback_markdown()

        return content

    except Exception as e:
        st.error("❌ Groq API call failed. Using generic questions instead.")
        st.caption(f"Details: {type(e).__name__}: {e}")
        return _generic_fallback_markdown()


# ==============================
# LLM helper – answer follow-up questions
# ==============================
def answer_followup(user_input: str) -> str:
    """
    Use Groq to answer user follow-up questions,
    staying in interview-prep context.
    """
    if client is None:
        return (
            "I can’t call the AI model right now, but you can still use the questions above "
            "to practice on your own. 😊"
        )

    tech_stack = st.session_state.candidate.get("tech_stack", "N/A")
    questions_md = st.session_state.latest_questions or "No questions."

    system_prompt = """
You are an interview preparation assistant.

You are chatting with a candidate AFTER you have already generated a set of
practice questions and mini-assignments for them.

Your job now:

- Answer their follow-up questions.
- Stay strictly focused on interview preparation, career advice, and their tech stack.
- You can explain concepts, give tips, or suggest how to approach the questions above.
- Be encouraging, concise, and practical.

IMPORTANT:
- Do NOT generate a brand new long list of questions.
- Do NOT talk about anything unrelated to interviews or tech career.
""".strip()

    user_context = f"""
Candidate tech stack: {tech_stack}

Practice set you already generated:

{questions_md}

Candidate just asked:

{user_input}
"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return (
            "Something went wrong while generating a response, "
            "but you can still use the questions above to practice. "
            f"(Error: {type(e).__name__})"
        )


# ==============================
# CONTACT FORM POPUP
# ==============================
def render_contact_form():
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)

        st.markdown("## 📮 Contact Us")
        st.markdown("Have a query or feedback? Fill this form and we’ll get back to you.")

        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Your Message / Query")

            submitted = st.form_submit_button("Submit")

        if submitted:
            if not name or not email or not message:
                st.warning("Please fill all the fields before submitting.")
            else:
                st.success("✅ Your query has been received! Our team will contact you soon.")
                st.session_state.show_contact = False

        if st.button("Close ❌"):
            st.session_state.show_contact = False

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()   # Only show contact form for this render


# ==============================
# Intro View
# ==============================
def render_intro():
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)

        # Header bar with contact button on the right
        col_l, col_r = st.columns([3, 1])
        with col_r:
            if st.button("📩 Contact us", key="contact_intro"):
                st.session_state.show_contact = True

        # Hero content with robot
        st.markdown(
            """
            <div style="text-align:center; padding: 10px 10px 20px 10px;">
                <div style="
                    width:90px; height:90px; margin:0 auto 12px auto;
                    border-radius:50%;
                    background: radial-gradient(circle at 30% 30%, #22d3ee, #4f46e5);
                    display:flex; align-items:center; justify-content:center;
                    box-shadow: 0 12px 30px rgba(0,0,0,0.6);
                    border: 2px solid rgba(148,163,184,0.7);
                ">
                    <span style="font-size:2.6rem;">🤖</span>
                </div>
                <h1 style="font-size: 2.1rem; margin-bottom: 0.3rem;">
                    TalentScout Hiring Assistant
                </h1>
                <p style="font-size: 1rem; opacity: 0.9; margin-bottom: 0.8rem;">
                    Practice your tech screening round like a real candidate – <b>powered by AI</b>.
                </p>
                <p style="font-size: 0.9rem; opacity: 0.85; margin-bottom: 1.2rem;">
                    Share your profile, and get tailored interview questions and mini-assignments based on your tech stack.
                </p>
                <div style="
                    display:inline-block;
                    padding: 8px 16px;
                    border-radius: 999px;
                    background: rgba(148,163,184,0.15);
                    color: #e5e7eb;
                    font-size: 0.85rem;
                    margin-bottom: 18px;
                ">
                    👀 Ready to see where you stand today?
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("✅ Let’s check you for today", use_container_width=True):
            st.session_state.view = "chat"
            if not st.session_state.history_messages:
                add_history(
                    "assistant",
                    (
                        "Hey there! 👋\n\n"
                        "I’m your **TalentScout Hiring Assistant**.\n\n"
                        "Fill out your basic details below, and I’ll generate "
                        "**practice interview questions** and **mini assignments** "
                        "tailored to your tech stack."
                    ),
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================
# Chat + Form View
# ==============================
def render_chat():
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)

        # Header row: title + Contact Us top-right
        col_left, col_right = st.columns([3, 1])
        with col_left:
            st.markdown("### 🤝 Candidate Screening – Practice Round")
        with col_right:
            if st.button("📩 Contact us", key="contact_chat"):
                st.session_state.show_contact = True

        # Small badge
        st.markdown(
            """
            <div style="
                padding: 6px 12px;
                border-radius: 999px;
                background: rgba(56,189,248,0.12);
                display:inline-flex;
                align-items:center;
                gap:8px;
                margin-bottom: 10px;
            ">
                <span>🧑‍💻</span>
                <span style="font-size:0.85rem;">Share your profile, get interview-style questions instantly.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # History as a separate section
        with st.expander("🕒 View conversation history (optional)", expanded=False):
            if not st.session_state.history_messages:
                st.write("No history yet. Start by filling the form below. 🙂")
            else:
                for msg in st.session_state.history_messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        st.divider()

        # 1️⃣ Candidate Details Form
        if st.session_state.stage in ["form", "questions"]:
            with st.expander("📋 Fill out your candidate details", expanded=True):
                with st.form("candidate_form"):
                    full_name = st.text_input("Full Name")
                    email = st.text_input("Email Address (Gmail only)")
                    phone = st.text_input("Phone Number (10 digits)")
                    years_exp = st.number_input(
                        "Years of Experience", min_value=0.0, step=0.5, format="%.1f"
                    )
                    desired_pos = st.text_input("Desired Position(s)")
                    location = st.text_input("Current Location")
                    tech_stack = st.text_area(
                        "Tech Stack (languages, frameworks, databases, tools)",
                        placeholder="e.g. Java, Python, Flutter, NLP, Computer Vision",
                    )

                    submitted = st.form_submit_button("🚀 Generate my practice interview")

                if submitted:
                    # Basic required fields
                    if not full_name or not email or not tech_stack:
                        st.warning(
                            "Please fill at least your **name**, a valid **Gmail address**, "
                            "and your **tech stack**."
                        )
                    else:
                        # Email validation: must be Gmail
                        if not email.lower().endswith("@gmail.com"):
                            st.error("Please enter a valid Gmail address (must end with @gmail.com).")
                        # Phone validation: if provided, must be 10 digits
                        elif phone and (not phone.isdigit() or len(phone) != 10):
                            st.error("Please enter a valid 10-digit phone number (numbers only).")
                        # Tech stack validation
                        elif not looks_like_tech_stack(tech_stack):
                            st.error(
                                "I’m not sure that looks like a tech stack yet. 🤔\n\n"
                                "Please enter skills like `Python, React, Flutter, NLP, SQL` "
                                "instead of a random sentence or request."
                            )
                        else:
                            # All good, continue
                            st.session_state.candidate = {
                                "full_name": full_name,
                                "email": email,
                                "phone": phone,
                                "years_experience": years_exp,
                                "desired_position": desired_pos,
                                "location": location,
                                "tech_stack": tech_stack,
                            }

                            add_history(
                                "assistant",
                                (
                                    f"Got it, **{full_name}**! I’ll generate a practice set based on "
                                    f"your tech stack: `{tech_stack}`."
                                ),
                            )

                            with st.spinner("Thinking up smart questions for you... 🧠"):
                                questions_md = generate_technical_questions_markdown(tech_stack)

                            st.session_state.latest_questions = questions_md
                            st.session_state.stage = "questions"

        st.divider()

        # 2️⃣ Show latest practice questions (always visible)
        if st.session_state.latest_questions:
            st.markdown("### 🎯 Your practice interview set")
            st.markdown(
                "These questions and mini-assignments are generated from your tech stack. "
                "Practice like a real round:"
            )
            st.markdown(st.session_state.latest_questions)

        # 3️⃣ LIVE CHAT AREA – show chat messages under the questions
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 4️⃣ Chat Input – follow-ups + bye
        user_input = st.chat_input("Ask something about your prep, or say bye to end...")

        if user_input:
            # Show user message in chat
            add_chat("user", user_input)

            # If user says bye / thanks → polite closing
            if is_end_keyword(user_input):
                goodbye = (
                    "You’re welcome! 💫\n\n"
                    "All the best for your interviews — you’ve got this. 🚀\n"
                    "Quick tips before you go:\n"
                    "- Practice answering out loud\n"
                    "- Time yourself for each question\n"
                    "- Note down gaps and revise those topics\n\n"
                    "See you soon, and good luck! 🍀"
                )
                add_chat("assistant", goodbye)
                st.session_state.stage = "ended"
            else:
                # After ending, keep it closed
                if st.session_state.stage == "ended":
                    add_chat(
                        "assistant",
                        "This session is already wrapped up. Refresh the page if you’d like "
                        "to start a fresh practice run. 🔁",
                    )
                # If form not done yet
                elif st.session_state.stage == "form":
                    add_chat(
                        "assistant",
                        "First, please fill out the form above so I can understand your profile. "
                        "Then I’ll generate practice questions for you. 📝",
                    )
                # During questions – answer follow-ups with LLM or fallback
                elif st.session_state.stage == "questions":
                    lower_q = user_input.lower()
                    if any(k in lower_q for k in OUT_OF_SCOPE_KEYWORDS):
                        add_chat(
                            "assistant",
                            "I’m not trained for that yet 🤖\n\n"
                            "Right now I only know how to help with **interview preparation** – "
                            "your tech stack, concepts, and how to answer questions.\n\n"
                            "If you need help, try asking things like:\n"
                            "- \"Can you explain question 2 in simple words?\"\n"
                            "- \"How should I structure an answer about OOP?\"\n"
                            "- \"What topics should I revise for this tech stack?\""
                        )
                    else:
                        reply = answer_followup(user_input)
                        add_chat("assistant", reply)

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================
# Main
# ==============================
if st.session_state.show_contact:
    render_contact_form()

if st.session_state.view == "intro":
    render_intro()
else:
    render_chat()
