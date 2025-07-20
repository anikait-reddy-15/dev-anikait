import json
import requests
import time
import os
import re

# === Configuration ===
API_URL = "https://4vemmwmcpb.ap-south-1.awsapprunner.com/structured_output/text"
INPUT_FILE = r"C:\Work Repos\dev-anikait\generated_questions.json"
TABLE_METADATA_FILE = r"C:\Work Repos\dev-anikait\refract\generate_planner\table_metada.json"
OUTPUT_DIR = "question_plans"
FAILED_LOG = "failed_questions.txt"
RAW_OUTPUT_LOG = "raw_outputs"
DELAY_BETWEEN_REQUESTS = 1
MAX_RETRIES = 3
TIMEOUT = 60  # seconds


def load_json_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_subtasks(raw_subtasks):
    if isinstance(raw_subtasks, list):
        return raw_subtasks
    if not isinstance(raw_subtasks, str):
        print("⚠️ 'subtasks' is neither a list nor a string.")
        return []

    try:
        # Strip whitespace and wrapping quotes if present
        cleaned = raw_subtasks.strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]

        # Fix common escape issues
        cleaned = cleaned.replace('\\"', '"').replace("\\n", " ").replace("\\t", " ").strip()

        # Try direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract just the JSON array
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)

    except Exception as e:
        print("⚠️ Final fallback JSON parse failed:", e)

    print("⚠️ Subtask returned output is empty")
    return []



def build_prompt_with_metadata(table_metadata):
    metadata_str = "\n".join(
        f"{table}: Description: {info['description']}, Columns: {info['columns']}"
        for table, info in table_metadata.items()
    )

    prompt = (
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
    return prompt


def send_to_api(question_text, prompt_template, question_index):
    payload = {
        "params": {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
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
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=TIMEOUT
            )

            if response.status_code in [502, 504]:
                print(f"⚠️ Gateway error {response.status_code} on attempt {attempt}. Retrying...")
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            data = response.json().get("data", {})

            # Save raw API response
            os.makedirs(RAW_OUTPUT_LOG, exist_ok=True)
            with open(os.path.join(RAW_OUTPUT_LOG, f"Q{question_index}_raw.json"), "w", encoding="utf-8") as raw_file:
                json.dump(data, raw_file, indent=2)

            subtasks_raw = data.get("subtasks")
            subtasks = parse_subtasks(subtasks_raw)

            if not subtasks:
                print("⚠️ Subtask returned output is empty")
                return {"question": question_text, "subtasks": []}

            normalized = []
            for step in subtasks:
                normalized.append({
                    "step": step.get("step"),
                    "task": step.get("task") or step.get("task_description"),
                    "table": step.get("table") or step.get("tables")
                })

            return {
                "question": data.get("question", question_text),
                "subtasks": normalized
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed on attempt {attempt}: {e}")
            time.sleep(2 ** attempt)

    return None


def log_failed_question(index, question_text):
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"Q{index}: {question_text}\n")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    questions = load_json_file(INPUT_FILE)
    table_metadata = load_json_file(TABLE_METADATA_FILE)
    prompt_template = build_prompt_with_metadata(table_metadata)

    for i, question in enumerate(questions["questions"], start=1):
        print(f"\n🚀 Processing Q{i}: {question}")
        result = send_to_api(question, prompt_template, i)

        if result:
            output_file = os.path.join(OUTPUT_DIR, f"Q{i}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"💾 Saved: {output_file}")
        else:
            print(f"⚠️ Skipped Q{i} due to repeated errors")
            log_failed_question(i, question)

        time.sleep(DELAY_BETWEEN_REQUESTS)


if __name__ == "__main__":
    main()