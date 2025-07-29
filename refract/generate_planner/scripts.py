import json
import requests
import time
import os
import tiktoken
import ast
import re

# === Configuration ===
API_URL = "https://4vemmwmcpb.ap-south-1.awsapprunner.com/structured_output/text"
INPUT_FILE = r"C:\Work Repos\dev-anikait\generated_questions.json"
TABLE_METADATA_FILE = r"C:\Work Repos\dev-anikait\refract\generate_planner\table_metada.json"
OUTPUT_DIR = "question_plans"
RAW_OUTPUT_LOG = "raw_responses"
MODEL_NAME = "gpt-4o-mini"
MAX_RETRIES = 3
TIMEOUT = 30

# === Cost Parameters (per million tokens) ===
COST_INPUT = 0.60 / 1e6
COST_OUTPUT = 2.40 / 1e6
COST_INPUT_CACHED = 0.30 / 1e6

# === Token Cost Tracking ===
token_total = 0
output_token_total = 0
cached_input_token_total = 0
input_token_total = 0
token_cache = {}

# === Subtask Parser ===
def parse_subtasks(raw_subtasks):
    if isinstance(raw_subtasks, list):
        return raw_subtasks
    if not isinstance(raw_subtasks, str):
        return []
    try:
        cleaned = raw_subtasks.strip().strip('"')
        cleaned = cleaned.replace('\\"', '"').replace("\\n", " ").replace("\\t", " ")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return ast.literal_eval(cleaned.replace("'", '"'))
    except Exception:
        return []

# === Tokenizer ===
def count_tokens(text, model="gpt-4o-mini"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

# === Prompt Construction ===
def build_prompt_with_metadata(table_metadata):
    metadata_str = "\n".join(
        f"{table}: Description: {info['description']}, Columns: {info['columns']}"
        for table, info in table_metadata.items()
    )
    return (
        "You are a smart SQL planner. Your job is to decompose business and IT questions into subtasks.\n"
        "You have access to the following database schema and metadata:\n\n"
        f"{metadata_str}\n\n"
        "For the given question, break it down into subtasks.\n"
        "Each subtask should contain:\n"
        "- step (integer step number)\n"
        "- task (description of the task)\n"
        "- table (list of relevant table names)\n\n"
        "Output JSON with keys: question (string), subtasks (list of objects with step, task, and table).\n"
        "Make sure to return at least minimum 3 meaningful subtasks\n"
        "You can include more than 3 if needed (e.g., 4, 5, 6...).\n"
        "Do not return an empty list.\n"
        "Use only tables provided in the schema\n"
        "Return only valid JSON.\n\n"
        "Question:\n{{question}}\n\n"
        "Output:"
    )

# === Send Question to API ===
def send_to_api(question_text, prompt_template, question_index):
    global token_total, output_token_total, token_cache
    global input_token_total, cached_input_token_total

    filled_prompt = prompt_template.replace("{{question}}", question_text)
    prompt_key = f"Q{question_index}"

    if prompt_key in token_cache:
        input_tokens = token_cache[prompt_key]["input_tokens"]
        cached_input_token_total += input_tokens
        print(f"📏 Q{question_index} input tokens (cached): {input_tokens}")
    else:
        input_tokens = count_tokens(filled_prompt, model=MODEL_NAME)
        token_cache[prompt_key] = {"input_tokens": input_tokens}
        input_token_total += input_tokens
        print(f"📏 Q{question_index} input tokens: {input_tokens}")

    token_total += input_tokens

    payload = {
        "params": {
            "provider": "openai",
            "model_name": MODEL_NAME,
            "prompt_template": prompt_template,
            "inputs": {"question": question_text},
            "output_schema": {
                "question": {"type": "str"},
                "subtasks": {
                    "type": "list",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step": {"type": "int"},
                            "task": {"type": "str"},
                            "table": {"type": "list", "items": {"type": "str"}}
                        }
                    }
                }
            }
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=payload, timeout=TIMEOUT)

            if response.status_code in [502, 504, 500]:
                print(f"⚠️ Server error {response.status_code} on attempt {attempt}. Retrying...")
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            data = response.json().get("data", {})

            os.makedirs(RAW_OUTPUT_LOG, exist_ok=True)
            raw_path = os.path.join(RAW_OUTPUT_LOG, f"Q{question_index}_raw.json")
            if not os.path.exists(raw_path):
                with open(raw_path, "w", encoding="utf-8") as raw_file:
                    json.dump(data, raw_file, indent=2)

            parsed_subtasks = parse_subtasks(data.get("subtasks", []))
            if not parsed_subtasks:
                print(f"⚠️ Skipped Q{question_index} due to empty or malformed subtasks.")
                return None

            data["subtasks"] = parsed_subtasks

            output_tokens = count_tokens(json.dumps(data), model=MODEL_NAME)
            output_token_total += output_tokens
            token_total += output_tokens
            print(f"📤 Q{question_index} output tokens: {output_tokens}")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed on attempt {attempt}: {e}")
            time.sleep(2 ** attempt)

    print(f"⚠️ Skipped Q{question_index} after {MAX_RETRIES} failed attempts.")
    return None

# === Main Execution ===
if __name__ == "__main__":
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    with open(TABLE_METADATA_FILE, "r", encoding="utf-8") as f:
        table_metadata = json.load(f)

    prompt_template = build_prompt_with_metadata(table_metadata)

    start_index = 5017
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, question in enumerate(questions["questions"], start=start_index):
        output_path = os.path.join(OUTPUT_DIR, f"Q{i}.json")
        raw_path = os.path.join(RAW_OUTPUT_LOG, f"Q{i}_raw.json")

        if os.path.exists(output_path):
            print(f"✅ Q{i} already processed. Skipping parsed JSON.")
            continue
        if os.path.exists(raw_path):
            print(f"✅ Q{i} already has raw response. Skipping request.")
            continue

        print(f"\n🚀 Processing Q{i}: {question}")
        result = send_to_api(question, prompt_template, i)

        if result:
            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(result, f_out, indent=2)

    print("\n=== Token Usage Summary ===")
    print(f"Input tokens (new): {input_token_total}")
    print(f"Input tokens (cached): {cached_input_token_total}")
    print(f"Output tokens: {output_token_total}")
    print(f"Total tokens: {token_total}")

    input_cost = input_token_total * COST_INPUT
    cached_input_cost = cached_input_token_total * COST_INPUT_CACHED
    output_cost = output_token_total * COST_OUTPUT
    total_cost = input_cost + cached_input_cost + output_cost

    print(f"Cost - Input (new): ${input_cost:.4f}")
    print(f"Cost - Input (cached): ${cached_input_cost:.4f}")
    print(f"Cost - Output: ${output_cost:.4f}")
    print(f"Total Estimated Cost: ${total_cost:.4f}")
