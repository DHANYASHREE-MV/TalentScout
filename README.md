

# ✨ **TalentScout – AI Interview Hiring Assistant**

🚀 *Your personal smart screening round, powered by Groq LLM + Streamlit*

---

## 🎯 **Overview**

**TalentScout** is an AI-powered hiring assistant that simulates a **real technical screening round**.
It collects the candidate’s profile, analyzes their **tech stack**, and generates **interview-style questions + mini assignments** using **Groq’s Llama-3.1-8B-Instant model**.

It also includes a **follow-up interview chat**, intelligent validation, and a modern UI — all deployed on **Streamlit Cloud**.

This project demonstrates your skills in:

* 🧠 LLM integration
* 💬 Chat-driven UX
* 🎛️ State management
* 🏗️ Frontend UI engineering with Streamlit
* 🔐 Secure API handling
* 🎨 Custom design & UX

---

## 🌟 **Features**

### ✅ **1. Dynamic Candidate Form**

Collects:

* Full Name
* Gmail-only email validation
* Phone number validation
* Experience
* Desired roles
* Location
* Tech stack (verified using intelligent keyword matching)

### ✅ **2. AI-Generated Interview Questions**

For every technology in the candidate’s stack, TalentScout generates:

* **3 tech-specific questions**
* **1 hands-on mini assignment**
* Clean **Markdown formatted** sections
* Automatic **fallback questions** if the LLM fails

### ✅ **3. Live AI Chat for Follow-Ups**

After generating the questions, the candidate can ask:

* “Explain question 2 in simple words”
* “How should I structure my answer for React hooks?”
* “What should I revise for SQL?”

LLM stays strictly in **interview mode** using a controlled system prompt.

### ❌ Out-of-scope requests get rejected politely

If user asks for:

* story, joke, weather, song, movie
  Assistant replies:
  **“I’m not trained for that yet — I only help with interview prep.”**

### ✅ **4. Conversation Memory (per session)**

* History view
* Live chat
* Clean session handling

### ✅ **5. Contact Form Popup**

A full-page popup form (NOT email) for feedback or queries.

### 🎨 **6. Modern UI & Custom Styling**

* Gradient background
* Glass-card effect
* Responsive layout
* Animated robot hero icon
* Stylish CTA buttons

---

## 🧠 **Tech Stack**

| Area             | Tools                           |
| ---------------- | ------------------------------- |
| Frontend / UI    | Streamlit                       |
| LLM              | Groq API (Llama-3.1-8B-Instant) |
| Environment      | Python 3                        |
| Secrets          | Streamlit Secrets / .env        |
| State Management | Streamlit Session State         |

---

## 🔐 **Environment Variables**

Create a `.env` (local only):

```
GROQ_API_KEY="your_key_here"
```

Or add in Streamlit Cloud:

```
GROQ_API_KEY="your_key_here"
```

---

## 🗂️ **Project Structure**

```
TalentScout/
│── app.py                # Main Streamlit app
│── requirements.txt      # Dependencies
│── .gitignore            # Ensures no secrets pushed
│── .streamlit/
│     └── secrets.toml    # (Local only – NOT committed)
```

---

## 🚀 **Run Locally**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## ☁️ **Deploy on Streamlit Cloud**

1. Push code to GitHub (no .env in repo)
2. Go to Streamlit → "New App"
3. Select the repo
4. Add Secrets:

```
GROQ_API_KEY="your_key"
```

5. Deploy 🎉

---

## 💡 **Why I Built This Project**

I built this to showcase how AI can improve hiring workflows by generating **structured, personalized technical interview rounds** automatically.

This project reflects my strengths in:

* AI/LLM engineering
* Full-stack ML apps
* Product-oriented problem solving
* UI/UX with Streamlit
* Secure deployment practices

---


---

## 🧑‍💻 **Author**

**Dhanyashree M V**
AI/ML Engineer • Full-Stack ML Developer
✨ Passionate about LLMs, intelligent systems, and building real products.

---



