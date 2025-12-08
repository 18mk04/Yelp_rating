# Yelp Rating Prediction + Two-Dashboard App

## Project Overview

This project implements a Yelp review analysis system with:
1. **Prompt Evaluation** - Testing different LLM prompts for star rating prediction
2. **User Dashboard** - Streamlit app for submitting reviews
3. **Admin Dashboard** - Streamlit app for managing and analyzing reviews
4. **FastAPI Backend** - API server with SQLite database and Gemini AI integration

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  User Dashboard │     │ Admin Dashboard │
│   (Streamlit)   │     │   (Streamlit)   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   FastAPI   │
              │   Backend   │
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
    │ SQLite  │ │ Gemini  │ │  Yelp   │
    │   DB    │ │   API   │ │  Data   │
    └─────────┘ └─────────┘ └─────────┘
```

## Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r user_dashboard/requirements.txt
pip install -r admin_dashboard/requirements.txt
pip install -r notebooks/requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
REVIEWS_DB=reviews.db
API_BASE=http://localhost:8000
```

### 4. Add Yelp Dataset

Download `yelp.csv` from Kaggle and place it in the `data/` folder.

## Running the Application

### Start Backend Server

```bash
cd backend
uvicorn app:app --reload --port 8000
```

### Start User Dashboard

```bash
cd user_dashboard
streamlit run user_app.py --server.port 8501
```

### Start Admin Dashboard

```bash
cd admin_dashboard
streamlit run admin_app.py --server.port 8502
```

## Task 1: Prompt Evaluation

Run the prompt evaluation script to test different prompting strategies:

```bash
cd notebooks
python rating_prompt_eval.py
```

This evaluates 4 prompt variants:
- **zero_shot**: Direct classification without examples
- **few_shot**: Classification with example reviews
- **cot_then_json**: Chain-of-thought reasoning before JSON output
- **strict_json**: Minimal JSON-only output format

Results are saved to `notebooks/outputs/`:
- `{variant}_raw.csv` - Detailed results per review
- `summary_metrics.csv` - Aggregated accuracy metrics

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/submit_review` | POST | Submit a new review with rating |
| `/reviews` | GET | List all reviews (with filters) |
| `/admin/summarize/{id}` | POST | Generate AI summary for a review |

## Project Structure

```
fynd/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── gemini_client.py    # Gemini API wrapper
│   └── requirements.txt
├── user_dashboard/
│   ├── user_app.py         # User-facing Streamlit app
│   └── requirements.txt
├── admin_dashboard/
│   ├── admin_app.py        # Admin Streamlit app
│   └── requirements.txt
├── notebooks/
│   ├── rating_prompt_eval.py  # Prompt evaluation script
│   └── requirements.txt
├── data/
│   └── yelp.csv            # Yelp dataset (not tracked)
├── docs/
│   └── README.md           # This file
└── .env                    # Environment variables (not tracked)
```
