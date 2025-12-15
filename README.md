# Yelp Rating Prediction and AI Review System

Author: Marikannan

## Overview
This project explores the use of Large Language Models (LLMs) for understanding and responding to customer reviews. It is divided into two main parts:

1. Rating prediction using prompt engineering
2. An AI-powered review response and management system

The backend is built using FastAPI and integrates Google Gemini for natural language generation.

---

## Task 1: Rating Prediction via Prompt Engineering

The first task evaluates how accurately an LLM can predict Yelp star ratings (1–5) using only review text.

### Prompt Variants
- Zero-shot prompting
- Few-shot prompting
- Chain-of-thought followed by JSON output
- Strict JSON-only prompting

### Evaluation Metrics
- JSON validity
- Accuracy on valid outputs
- Overall accuracy

Due to free-tier API limits, large-scale evaluation was constrained, but the experiment highlights how prompt structure impacts output reliability.

---

## Task 2: AI-Powered Review System

The second task focuses on building a practical application.

### Features
- Submit reviews with star ratings
- Automatically generate friendly AI responses
- Store reviews in a database
- Admin endpoints for summaries and action suggestions

---

## Tech Stack
- Python
- FastAPI
- SQLite
- Google Gemini API
- Render (deployment)

---

## Live Demo
Backend API is deployed at:

https://yelp-rating-1.onrender.com

Interactive API docs:

https://yelp-rating-1.onrender.com/docs

---

## How to Run Locally

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
