# notebooks/rating_prompt_eval.py

import os, json, time
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
# DATA LOADING
# -----------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "yelp.csv")
SAMPLE_N = 200

df = pd.read_csv(DATA_PATH)

text_col = "text" if "text" in df.columns else ("review" if "review" in df.columns else df.columns[0])
star_col = "stars" if "stars" in df.columns else ("rating" if "rating" in df.columns else df.columns[1])

df = df[[text_col, star_col]].dropna().rename(columns={text_col: "text", star_col: "stars"})
df_sample = df.sample(SAMPLE_N, random_state=42).reset_index(drop=True)

# -----------------------------
# PROMPT VARIANTS
# -----------------------------
PROMPTS = {
    "zero_shot": {
        "system": (
            "You are an assistant that classifies Yelp reviews into a star rating from 1 to 5. "
            "Return exactly one JSON object: {\"predicted_stars\": <int>, \"explanation\": \"<reason>\"}. "
            "No extra text."
        ),
        "user": 'Review: "{text}"\n\nReturn the required JSON.'
    },

    "few_shot": {
        "system": "You are an assistant that returns exactly one JSON object per review.",
        "user": '''Example 1:
Review: "The food was absolutely delicious and the server was friendly. We will come back!"
Output:
{{"predicted_stars": 5, "explanation": "Very positive experience"}}

Example 2:
Review: "Waited 45 minutes, food was cold. Manager never apologized."
Output:
{{"predicted_stars": 1, "explanation": "Very negative experience"}}

Now classify this review:
"{text}"

Output:'''
    },

    "cot_then_json": {
        "system": (
            "List 2 short observations, then output exactly one JSON object at the end: "
            "{{\"predicted_stars\": <int>, \"explanation\": \"<reason>\"}}"
        ),
        "user": 'Review: "{text}"\n\nBegin analysis and end with JSON only.'
    },

    "strict_json": {
        "system": (
            "You are a JSON-only classifier. Output ONLY a valid single-line JSON: "
            "{{\"predicted_stars\": <int>, \"explanation\": \"<text>\"}}"
        ),
        "user": 'Classify this review: "{text}"'
    }
}

# -----------------------------
# GEMINI CLIENT SETUP
# -----------------------------
from google import genai

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY missing. Add it to .env")

client = genai.Client(api_key=API_KEY)

# -----------------------------
# GEMINI CALL FUNCTION (WORKING)
# -----------------------------
def call_gemini(system_prompt, user_prompt):
    full_prompt = system_prompt + "\n\n" + user_prompt

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[full_prompt],   # MUST be a list
    )

    return response.text or ""


# -----------------------------
# JSON PARSER
# -----------------------------
def parse_json_from_text(s):
    if not s or not isinstance(s, str):
        return None

    s = s.strip()

    try:
        start = s.index('{')
        end = s.rindex('}') + 1
        obj = json.loads(s[start:end])
        return obj
    except Exception:
        return None


# -----------------------------
# EVALUATION LOOP
# -----------------------------
output_dir = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(output_dir, exist_ok=True)

summary_rows = []

for variant, tmpl in PROMPTS.items():
    print(f"\nRunning variant: {variant}")
    records = []

    for _, row in tqdm(df_sample.iterrows(), total=len(df_sample), desc=variant):
        text = row['text'].replace('"', '\\"')

        system_prompt = tmpl["system"]
        user_prompt   = tmpl["user"].format(text=text)

        try:
            raw = call_gemini(system_prompt, user_prompt)
        except Exception:
            raw = ""

        parsed = parse_json_from_text(raw)
        valid = parsed is not None and isinstance(parsed.get("predicted_stars"), int)
        pred  = parsed.get("predicted_stars") if parsed else None

        records.append({
            "text": row["text"],
            "true_star": int(row["stars"]),
            "raw": raw,
            "valid_json": valid,
            "pred_star": pred,
            "explanation": parsed.get("explanation") if parsed else None
        })

        time.sleep(0.20)  # polite delay

    df_out = pd.DataFrame(records)
    df_out.to_csv(os.path.join(output_dir, f"{variant}_raw.csv"), index=False)

    total = len(df_out)
    valid_count = df_out["valid_json"].sum()
    correct_valid = ((df_out["pred_star"] == df_out["true_star"]) & df_out["valid_json"]).sum()
    correct_overall = (df_out["pred_star"] == df_out["true_star"]).sum()

    summary_rows.append({
        "variant": variant,
        "json_validity": valid_count / total,
        "accuracy_valid": correct_valid / valid_count if valid_count else 0,
        "accuracy_overall": correct_overall / total
    })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(os.path.join(output_dir, "summary_metrics.csv"), index=False)

print("\nDONE! Results saved in notebooks/outputs/")
