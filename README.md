# Yelp Rating Prediction and AI Review System

Author: Marikannan

---

## Overview

This project explores how Large Language Models (LLMs) can be used to understand, classify, and respond to customer reviews in a practical application.

The work is divided into two main parts:

1. Predicting Yelp-style star ratings (1–5) from review text using prompt engineering  
2. Building a small end-to-end review management system with AI-generated responses, summaries, and recommendations

The backend is implemented using FastAPI, and Google Gemini is used for all language generation tasks. The system is deployed using Render.

---

## Project Structure

- `backend/`  
  FastAPI application, database logic, and Gemini client

- `notebooks/`  
  Experiments for prompt-based rating prediction and evaluation

- `user_dashboard/`  
  Streamlit application for public users to submit reviews

- `admin_dashboard/`  
  Streamlit application for administrators to monitor and analyze reviews

---

## Task 1: Rating Prediction via Prompt Engineering

The goal of Task 1 is to evaluate how effectively an LLM can predict star ratings based only on the textual content of a review.

### Prompt Variants Tested

Four prompt styles were implemented and evaluated:

- **Zero-shot**  
  The model is asked directly to predict the rating without examples.

- **Few-shot**  
  A small number of labeled examples are provided before prediction.

- **Chain-of-thought + JSON**  
  The model is instructed to reason briefly before producing structured output.

- **Strict JSON**  
  The model is constrained to return only valid JSON with no additional text.

### Evaluation Metrics

Model outputs were evaluated using:

- **JSON Validity** – whether the output could be parsed successfully  
- **Accuracy (Valid Only)** – accuracy on valid JSON outputs  
- **Overall Accuracy** – accuracy across all samples

### Observations

Due to free-tier API limits and strict output constraints, large-scale evaluation was limited.  
The zero-shot prompt showed partial success, while more constrained prompts struggled under quota and formatting restrictions.

These results highlight how sensitive LLM behavior can be to prompt structure and output constraints.

---

## Task 2: AI-Powered Review System

Task 2 focuses on building a practical, production-style system that integrates LLMs into a real workflow.

### Core Features

- Users can submit a star rating and written review
- An AI-generated response is returned immediately
- Reviews are stored in a shared database
- Administrators can:
  - View all submissions
  - Generate AI summaries
  - Receive AI-suggested recommended actions
  - View basic rating analytics

Both dashboards interact with the same backend and data source.

---

## Technology Stack

- Python
- FastAPI
- SQLite
- Google Gemini API
- Streamlit
- Render (deployment)

---

## Live Deployment

### Backend API

Base URL:  
https://yelp-rating.onrender.com

Interactive API documentation:  
https://yelp-rating.onrender.com/docs
---

## Dashboards

### User Dashboard 

The user dashboard allows customers to:

- Select a star rating
- Write a short review
- Submit feedback
- Receive an AI-generated response

Live URL:  
    https://user-dashboard-87kd.onrender.com

---

### Admin Dashboard 

The admin dashboard provides:

- A live list of all reviews
- Rating distribution analytics
- AI-generated summaries
- AI-recommended actions for each review

Live URL:  
    https://admin-dashboard-b4mq.onrender.com

> Both dashboards communicate with the same FastAPI backend and shared database.

---
