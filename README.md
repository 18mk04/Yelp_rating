# AI-Powered Review Analysis and Management System

This project focuses on using a Large Language Model (Gemini) to work with customer reviews in a practical way. The idea was not just to call an LLM, but to understand how prompt design affects outputs and how AI can be integrated into a small real-world application.

The project is split into two parts:
- Task 1: Predicting Yelp star ratings from review text using prompt engineering
- Task 2: Building a simple review system with AI-generated responses, summaries, and actions


## Task 1: Rating Prediction Using Prompt Engineering

The goal of this task was to check whether an LLM can correctly predict Yelp star ratings (1–5) using only the review text.

Instead of training a model, different prompt styles were tested.

### Prompt styles tested

- **Zero-shot** – Directly asking the model to predict the rating  
- **Few-shot** – Providing example reviews with ratings before prediction  
- **Chain-of-thought + JSON** – Asking the model to reason briefly and then output JSON  
- **Strict JSON** – Forcing the model to return only structured JSON  

### Evaluation metrics

- JSON validity (whether output could be parsed)
- Accuracy on valid outputs
- Overall accuracy

### Results summary

| Prompt Type     | JSON Validity | Accuracy (Valid) | Overall Accuracy |
|-----------------|--------------|------------------|------------------|
| Zero-shot       | 0.09         | 0.61             | 0.055            |
| Few-shot        | 0.00         | 0.00             | 0.00             |
| CoT + JSON      | 0.00         | 0.00             | 0.00             |
| Strict JSON     | 0.00         | 0.00             | 0.00             |

Because of strict output constraints and free-tier API limits, only the zero-shot prompt produced usable results.

---

## Task 2: AI-Powered Review System

This part of the project focuses on building a working system rather than evaluation.

### What it does

- Users submit a star rating and written review
- The backend generates a friendly AI response
- Reviews are stored in a database
- Admins can view reviews and trigger:
  - Short summaries
  - Recommended next actions

### Technology used

- FastAPI (backend)
- SQLite (database)
- Gemini LLM (text generation)
- Python-based dashboards
- Render (deployment)

---

## Deployment
The backend is deployed on Render.
Environment variables are configured directly in the Render dashboard.

## Limitations
Free-tier Gemini API limits restrict large-scale testing

Strict JSON output is difficult to enforce with generative models

Rating prediction accuracy depends heavily on prompt wording

## Future Improvements
Better batching and retry logic for API calls

Use of fine-tuned or hybrid classification models

Scalable database instead of SQLite

Authentication for admin access


# Author
Marikannan
