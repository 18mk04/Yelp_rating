# notebooks/rating_prompt_eval.py
import os, json, time
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "yelp.csv")
SAMPLE_N = 200

# Load dataset
df = pd.read_csv(DATA_PATH)
text_col = "text" if "text" in df.columns else ("review" if "review" in df.columns else df.columns[0])
star_col = "stars" if "stars" in df.columns else ("rating" if "rating" in df.columns else df.columns[1])
df = df[[text_col, star_col]].dropna().rename(columns={text_col:"text", star_col:"stars"})
df_sample = df.sample(SAMPLE_N, random_state=42).reset_index(drop=True)

PROMPTS = {
  "zero_shot": {
    "system": "You are an assistant that classifies Yelp reviews into a star rating from 1 to 5. Return exactly one JSON object: {\"predicted_stars\": <int 1-5>, \"explanation\": \"<1-2 sentence reasoning>\"}. No extra text.",
    "user": 'Review: "{text}"\n\nReturn the required JSON.'
  },
  "few_shot": {
    "system": "You are an assistant that returns exactly one JSON object per review.",
    "user": '''Example 1:
Review: "The food was absolutely delicious and the server was friendly. We will come back!"
Output:
{"predicted_stars": 5, "explanation": "Very positive words about food and service, clear intent to return."}

Example 2:
Review: "Waited 45 minutes, food was cold and bland. Manager never apologized."
Output:
{"predicted_stars": 1, "explanation": "Long wait, cold food, no apology — clear dissatisfaction."}

Now classify:
Review: "{text}"

Output:'''
  },
  "cot_then_json": {
    "system": "List 2 short observations, then output exactly one JSON object on the last line: {\"predicted_stars\":.., \"explanation\":...}",
    "user": 'Review: "{text}"\n\nAnalyze and output observations followed by the JSON.'
  },
  "strict_json": {
    "system": "You are a JSON-only classifier. Output a single-line JSON that matches schema: predicted_stars int 1-5, explanation string. No extra fields or text.",
    "user": 'Classify this review: "{text}"'
  }
}

def call_gemini(system_prompt, user_prompt):
    """
    Replace this function with your Gemini API call.
    Must return the model text as a string.
    """
    raise NotImplementedError("Replace call_gemini with your Gemini API call")

def parse_json_from_text(s):
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    try:
        start = s.index('{')
        end = s.rindex('}') + 1
        j = json.loads(s[start:end])
        return j
    except Exception:
        return None

os.makedirs(os.path.join(os.path.dirname(__file__), "outputs"), exist_ok=True)
summary_rows = []
for variant, tmpl in PROMPTS.items():
    records = []
    for _, r in tqdm(df_sample.iterrows(), total=len(df_sample), desc=variant):
        text = r['text'].replace('"','\\"')
        user_prompt = tmpl['user'].format(text=text)
        system_prompt = tmpl['system']
        try:
            raw = call_gemini(system_prompt, user_prompt)
        except Exception as e:
            raw = ""
        parsed = parse_json_from_text(raw)
        valid = parsed is not None and isinstance(parsed.get("predicted_stars", None), int)
        pred = parsed.get("predicted_stars") if parsed else None
        records.append({
            "text": r['text'],
            "true_star": int(r['stars']),
            "raw": raw,
            "valid_json": valid,
            "pred_star": pred,
            "explanation": parsed.get("explanation") if parsed else None
        })
        time.sleep(0.25)
    df_out = pd.DataFrame(records)
    df_out.to_csv(os.path.join(os.path.dirname(__file__), "outputs", f"{variant}_raw.csv"), index=False)
    total = len(df_out)
    valid_count = df_out['valid_json'].sum()
    correct_valid = ((df_out['pred_star'] == df_out['true_star']) & df_out['valid_json']).sum()
    correct_overall = (df_out['pred_star'] == df_out['true_star']).sum()
    summary_rows.append({
        "variant": variant,
        "json_validity": valid_count/total,
        "accuracy_valid": correct_valid / valid_count if valid_count else 0,
        "accuracy_overall": correct_overall/total
    })

pd.DataFrame(summary_rows).to_csv(os.path.join(os.path.dirname(__file__), "outputs", "summary_metrics.csv"), index=False)
print("Done. See notebooks/outputs/*.csv")
