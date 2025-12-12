# 🏏 The Wicket-Down Downtime: T20 World Cup vs. Indian Dev Productivity

> *"Production deployments stop when Kohli is batting"* - Every Indian Engineering Manager, probably

## 🎯 The Hook

Ever wondered if the entire Indian tech ecosystem collectively holds its breath when a wicket falls during a crucial cricket match? This project proves what we've all suspected: **cricket matches have a measurable impact on global developer productivity**.

When Virat Kohli gets out, do GitHub commits drop by 40%? When India wins the T20 World Cup, does the commit graph look like a flatline? We're about to find out.

## 🚀 The Challenge

Built for the **AI for Bharat: The Data Weaver Challenge** - the ultimate test of mashing up two completely unrelated data sources:

- 🏏 **Cricket Data**: Ball-by-ball commentary from the T20 World Cup Final 2024 (via Cricsheet)
- 💻 **GitHub Data**: Real-time global commit volume during the match (via GitHub Search API)

The goal? Prove that cricket isn't just a game - it's a force that shapes the digital world.

## 🛠️ The Stack

- **Python** - The backbone of our data pipeline
- **Streamlit** - Interactive dashboard that makes data beautiful
- **Pandas** - Data wrangling and time-series alignment
- **Plotly** - Interactive charts that tell the story
- **Kiro (Agentic IDE)** - The secret weapon that made this 10x faster

## ⚡ Kiro Implementation: Spec-Driven Development at Warp Speed

This project showcases the power of **Kiro's Spec-Driven Development** methodology. Instead of jumping straight into code, we:

1. **Defined Clear Specs**: Three focused specification files in `specs/` that break down the entire project
2. **Automated Quality Checks**: Smart agent hooks in `.kiro/hooks/` that catch issues before they become problems
3. **Iterative Development**: Each spec builds on the previous one, ensuring clean architecture

### 🤖 Agent Hooks in Action

The `.kiro/hooks/` directory contains intelligent automation:

- **`data_integrity.yaml`**: Automatically validates data correlation whenever analysis scripts are saved
- **`security_check.yaml`**: Prevents accidental token commits (because we've all been there)
- **`plot_generator.yaml`**: Streamlines chart generation workflow

These hooks act as your AI pair programmer, catching issues and maintaining code quality without manual intervention.

### 📋 Spec-Driven Architecture

```
specs/
├── 01_data_ingestion.md    # Cricket + GitHub data fetching
├── 02_normalization.md     # Time alignment and processing  
└── 03_dashboard_ui.md      # Streamlit visualization
```

Each spec file contains detailed requirements, acceptance criteria, and implementation guidelines - making the development process predictable and efficient.

## 🚀 Quick Setup Guide

### ⚡ Super Quick Start (Recommended)
```bash
git clone <your-repo-url>
cd wicket-down-downtime
python quick_start.py
```
This will install dependencies, create sample data, and launch the dashboard automatically!

### 📋 Manual Setup

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd wicket-down-downtime
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Choose Your Data Source

**For Testing (No GitHub Token Required):**
```bash
python src/create_sample_data.py
```

**For Real Data (GitHub Token Required):**
```bash
cp .env.example .env
# Edit .env and add: GITHUB_TOKEN="your_github_token_here"
```

> **Getting a GitHub Token**: Go to GitHub Settings → Developer Settings → Personal Access Tokens → Generate new token. No special permissions needed for public repo search.

### 4. Choose Your Data Source

**Option A: Use Sample Data (Quick Start)**
```bash
# Generate sample data for immediate testing
python src/create_sample_data.py
```

**Option B: Use Real Data (Requires GitHub Token)**
```bash
# Fetch cricket data
python src/ingest_cricket.py

# Fetch GitHub commit data (this takes ~10 minutes due to API rate limits)
python src/ingest_github.py

# Process and align the datasets
python src/process_data.py
```

**Option C: Run Complete Pipeline**
```bash
# Automated pipeline (checks requirements and runs all steps)
python run_pipeline.py
```

### 5. Launch the Dashboard
```bash
streamlit run src/app.py
```

Visit `http://localhost:8501` to see the magic happen!

## 📸 Screenshots

### The Main Dashboard
*[Screenshot placeholder: Full dashboard showing both cricket timeline and commit volume]*

### Wicket Impact Analysis
*[Screenshot placeholder: Close-up of commit drop when a wicket falls]*

### Interactive Tooltips
*[Screenshot placeholder: Hover effects showing correlation data]*

## 🎯 Key Features

- **Real-time Correlation**: See exactly how cricket events impact global developer activity
- **Interactive Timeline**: Hover over wickets to see immediate productivity impact
- **Dual-axis Visualization**: Cricket runs vs. GitHub commits on synchronized timelines
- **Smart Data Alignment**: Sophisticated time-series merging using pandas
- **Rate-limit Handling**: Robust GitHub API integration with proper throttling

## 🏗️ Project Structure

```
├── specs/                  # Specification-driven development
│   ├── 01_data_ingestion.md
│   ├── 02_normalization.md
│   └── 03_dashboard_ui.md
├── src/
│   ├── data/              # Generated datasets (gitignored)
│   ├── ingest_cricket.py  # Cricsheet data processor
│   ├── ingest_github.py   # GitHub API client
│   ├── process_data.py    # Data alignment and normalization
│   └── app.py            # Streamlit dashboard
├── .kiro/
│   └── hooks/            # Automated quality checks
└── tests/                # Data validation tests
```

## 🤝 Contributing

This project demonstrates modern development practices:

1. **Spec-First Development**: All features start with clear specifications
2. **Automated Quality Gates**: Kiro hooks ensure code quality
3. **Data-Driven Insights**: Every visualization tells a story

Feel free to contribute additional data sources, visualization improvements, or extend the analysis to other sports!

## 📊 The Hypothesis

We believe that major cricket events create measurable dips in global developer productivity, especially from Indian developers. This project provides the data to prove (or disprove) this theory.

**Spoiler Alert**: The results might surprise you! 🏏📈

## 🚀 GitHub Repository Setup

This repository is designed to be public and includes:

- ✅ **Complete source code** in `src/`
- ✅ **Kiro agent hooks** in `.kiro/hooks/`
- ✅ **Specification files** in `specs/`
- ✅ **Sample data generator** for testing
- ❌ **Real data files** (excluded via .gitignore)
- ❌ **Environment secrets** (.env file excluded)

### For Contributors:
1. Fork this repository
2. Create your `.env` file with GitHub token
3. Run `python src/create_sample_data.py` for quick testing
4. Or use real data with `python run_pipeline.py`

### Repository Structure:
```
├── .kiro/                  # Kiro agent configuration (INCLUDED)
├── src/                    # Source code (INCLUDED)
├── specs/                  # Specifications (INCLUDED)
├── tests/                  # Data validation (INCLUDED)
├── requirements.txt        # Dependencies (INCLUDED)
├── .env.example           # Environment template (INCLUDED)
├── .gitignore             # Git exclusions (INCLUDED)
└── src/data/              # Data files (EXCLUDED from git)
```

---

*Built with ❤️ and Kiro's Agentic IDE for the AI for Bharat Challenge*