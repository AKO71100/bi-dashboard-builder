# 📊 BI Dashboard Builder

> **AI-powered business intelligence tool** — upload any CSV/Excel file and get instant charts, statistical analysis, and AI-generated executive summaries. No coding required.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-purple?logo=plotly&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq%20%2F%20LLaMA-orange)
![License](https://img.shields.io/badge/License-MIT-green)
[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bi-dashboard-builder.streamlit.app/)

---

## ✨ Key Features

| Module | What it does |
|---|---|
| **📁 Data Upload** | CSV (auto-detect separator) and Excel (.xlsx/.xls); schema preview, null/duplicate diagnostics |
| **🧹 Data Cleaning** | Drop nulls/duplicates, fill missing values (mean/median/mode/constant), type conversion, outlier removal |
| **📐 Statistical Analysis** | Descriptive stats, A/B test (t-test + proportion z-test), correlation matrix, funnel analysis, cohort retention, **RFM segmentation** |
| **🤖 AI Chart Generator** | Natural language → Plotly chart via Groq LLaMA; 8 quick-prompt templates; save chart gallery |
| **📦 Export** | Download CSV, generate standalone HTML report (3 themes), **AI Executive Summary** in RU/EN/PL |

---

## 🖥️ Screenshots

> _Add screenshots here after first deploy (see **Contributing** section below)_

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/bi-dashboard-builder.git
cd bi-dashboard-builder
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run bi_app.py
```

The app will open automatically at `http://localhost:8501`

---

## 🔑 Groq API Key (optional but recommended)

The AI chart generator and Executive Summary require a **free** Groq API key.

1. Go to [console.groq.com](https://console.groq.com) → create an account
2. Generate an API key (it's free, no credit card needed)
3. Paste the key into the sidebar field **🔑 Groq API**

> **Without a key:** data upload, cleaning, statistical analysis, and manual chart builder still work fully.

---

## 📦 Dependencies

```
streamlit>=1.35
pandas>=2.0
numpy>=1.24
plotly>=5.18
scipy>=1.11
statsmodels>=0.14
openpyxl>=3.1
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🗂️ Project Structure

```
bi-dashboard-builder/
├── bi_app.py           # Main application (~1900 lines)
├── requirements.txt    # Python dependencies
├── README.md
└── sample_data/        # (optional) example CSV files for testing
```

---

## 📐 Analysis Modules — Details

### A/B Testing
- **Continuous metrics** (revenue, time spent): Welch t-test, Cohen's d effect size
- **Proportions** (conversion rate, CTR): z-test, confidence intervals
- Automatic significance interpretation (p-value with α=0.05)

### RFM Segmentation
Classifies customers into 7 segments: **Champions · Loyal · New · Big Spenders · At Risk · Lost · Regular**  
Based on Recency / Frequency / Monetary quintile scoring.

### Cohort Retention
Monthly cohort matrix with heatmap and average retention curve.

### AI Chart Generator
Sends column names + natural language query to Groq LLaMA → receives Python/Plotly code → executes and renders. Supports: bar, line, pie, scatter, histogram, box, funnel, heatmap.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit + custom CSS (glassmorphism dark theme)
- **Charts:** Plotly Express & Graph Objects
- **Statistics:** SciPy, Statsmodels
- **AI/LLM:** Groq API (LLaMA 3.3 70B / LLaMA 3.1 / Mixtral / DeepSeek R1)
- **Data:** Pandas + NumPy

---

## 🌐 Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub → select repo → set main file: `bi_app.py`
4. Click **Deploy**

Your app gets a public URL like `https://your-app.streamlit.app` — perfect for sharing in a portfolio.

---

## 📄 License

MIT — free to use, modify, and distribute.

---

## 👤 Author

**Andrii** · [github.com/AKO71100](https://github.com/AKO71100)

> Part of a portfolio focused on AI automation, data analytics, and Python tooling.  
> Other projects: [TTS Studio](https://github.com/AKO71100/tts-studio)
