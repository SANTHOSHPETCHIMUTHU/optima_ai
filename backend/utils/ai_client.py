import json
import re
from openai import OpenAI

def get_openrouter_client(api_key: str) -> OpenAI:
    """
    Initializes and returns the Groq OpenAI-compatible client.
    """
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key.strip()
    )

def plan_prompt(fingerprint: dict, max_steps: int = 15) -> str:
    """
    Constructs the specialized system instruction prompt for "DataClean-Agent",
    modeled after Julius AI's methodology.
    """
    return f"""
You are "DataClean-Agent", an autonomous data-analysis and cleaning agent modeled after Julius AI's real-world data-cleaning workflow. Your task is to analyze, detect, clean, and describe dataset issues exactly as Julius AI does.

========================
AGENT RULES & CONSTRAINTS
========================
- Always analyze the data before cleaning.
- Always produce a reversible cleaning plan.
- Never remove data without justification.
- Assume user wants "Julius-like full cleaning" unless specified.
- Be transparent: explain each transformation.
- Use multi-step reasoning.
- Never hallucinate data; operate strictly on provided tables.

========================
CORE BEHAVIOR MODEL
========================
Follow Julius AI's documented cleaning workflow:
1. Perform an automatic initial scan:
   - Detect inconsistent formatting, missing entries, duplicate rows.
   - Identify dirty columns and potential schema problems.

2. Generate a complete column-level profile:
   - Infer column types (numeric, categorical, datetime, boolean, text).
   - Identify pattern consistency, null counts, unique counts.

3. Detect problems:
   - Missing data patterns, type mismatches.
   - Category inconsistencies (e.g. "US", "U.S.A.", "United States").
   - Duplicates, outliers, formatting inconsistencies.

========================
CLEANING WORKFLOW
========================
Follow Julius AI's multi-step cleaning logic:
1. Fix formatting (standardize case, whitespace).
2. Drop unneeded/leftover index columns using "drop_columns".
3. Extract precise numbers from strings (e.g. "8GB" -> 8, "1.2kg" -> 1.2) using "extract_numeric".
4. Extract advanced features (e.g. Parse Memory into SSD/HDD, extract CPU/GPU brands) using "regex_extract" with "pattern" and a "new_columns" list.
5. Standardize categories & OS names using "map_categories" with a "mapping" dict {{"TargetName": ["variant1", "variant2"]}}.
6. Handle missing values (impute median/mode or drop responsibly).
7. Remove exact and near duplicates.
8. Remove impossible outliers strictly using "filter_range" (e.g., negative prices, impossible weights) or "outliers_iqr".
9. Type correction exactly.

========================
OUTPUT & EXPLANATION REQUIREMENTS
========================
Your outputs must include MULTIPLE PARTS:

A. A structured JSON cleaning plan (in a markdown ```json block):
   - You MUST provide a valid JSON object with an "actions" key.
   - Each action in "actions" MUST have a "type" string from the allowed list: 
     "normalize_columns", "strip_whitespace", "drop_empty_rows", "drop_empty_cols", "deduplicate", "coerce_numeric", "parse_dates", "standardize_categories", "outliers_iqr", "drop_high_null_cols", "impute", "drop_columns", "extract_numeric", "regex_extract", "map_categories", "filter_range".
   - Each action should include a "params" object if applicable (e.g. "columns", "mapping", "pattern").
   - DO NOT omit the JSON block. It is CRITICAL for the pipeline.

B. A natural-language explanation (Julius-style):
   - Describe what was wrong in a professional, concise manner.
   - Explain cleaning choices clearly and simply.
   - Summarize the improvements made.

C. Expected result summary text.

Dataset Fingerprint:
{json.dumps(fingerprint)}
"""

def _robust_parse_json(raw: str) -> dict:
    """
    Attempt to parse a JSON string produced by an LLM, applying progressive
    auto-fix strategies to recover from common AI mistakes.
    """
    # Strategy 1: parse as-is
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Strategy 2: remove trailing commas before ] or }
    # e.g.  {"a": 1,}  or  [1, 2,]
    cleaned = re.sub(r",\s*([}\]])", r"\1", raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: replace Python-style single-quoted strings with double-quoted.
    # Naively swap outer single-quotes that wrap values, being careful not to
    # touch apostrophes inside words.
    cleaned2 = re.sub(r"(?<![\\])'", '"', cleaned)
    # Also replace Python literals True/False/None
    cleaned2 = cleaned2.replace("True", "true").replace("False", "false").replace("None", "null")
    try:
        return json.loads(cleaned2)
    except json.JSONDecodeError:
        pass

    # Strategy 4: strip any control characters / literal newlines inside string values
    cleaned3 = re.sub(r'(?<=")([^"\\]*(?:\\.[^"\\]*)*)"', 
                      lambda m: m.group(0).replace('\n', ' ').replace('\r', ' '), 
                      cleaned2)
    try:
        return json.loads(cleaned3)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not repair malformed JSON from AI: {e}") from e


def request_plan(client: OpenAI, prompt: str) -> tuple[dict, str]:
    """
    Sends the generated dataset payload to the AI, safely extracting BOTH
    the JSON structural plan and the conversational explanation block.
    Falls through ALL models on any error (rate-limit OR parse error) so a
    malformed response from model #1 automatically retries with model #2.
    """
    ALL_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]

    last_error = "Unknown error"

    for model in ALL_MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            full_content = resp.choices[0].message.content.strip()

            # ── Extract the first ```json ... ``` block ──
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", full_content, re.DOTALL)
            if json_match:
                plan_str = json_match.group(1).strip()
            elif full_content.startswith("{") and full_content.endswith("}"):
                # The entire response might be raw JSON
                plan_str = full_content
            else:
                # No JSON block at all — try next model
                last_error = f"No JSON block found in response from {model}"
                print(f"DEBUG [request_plan]: {last_error}")
                continue

            # ── Robust parse (auto-fixes common AI JSON issues) ──
            plan = _robust_parse_json(plan_str)

            # Sanitise actions list
            if isinstance(plan, dict) and "actions" in plan and isinstance(plan["actions"], list):
                plan["actions"] = [
                    a for a in plan["actions"]
                    if isinstance(a, dict) and isinstance(a.get("type"), str) and a["type"].strip()
                ]

            # Explanation = everything outside the markdown block
            explanation = re.sub(r"```(?:json)?\s*\{.*?\}\s*```", "", full_content, flags=re.DOTALL).strip()
            if not explanation:
                explanation = f"Cleaned the dataset based on the generated plan using {model}."

            return plan, explanation

        except Exception as e:
            err_str = str(e)
            last_error = err_str
            print(f"DEBUG [request_plan] {model} failed: {err_str[:200]}")
            # Always try the next model — whether it's a rate-limit OR a parse error
            continue

    # All models exhausted
    raise RuntimeError(
        f"All AI models failed to produce a valid cleaning plan. Last error: {last_error}"
    )
