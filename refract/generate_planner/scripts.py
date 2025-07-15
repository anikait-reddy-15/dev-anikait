import openai
import json
import os
from dotenv import load_dotenv
from time import sleep
import re

load_dotenv()
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def chunk_list(lst, chunk_size):
    """Split a list into chunks of a specific size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def clean_question(q):
    """Remove leading numbering and (Tables: ...) part from the question."""
    q = q.strip()
    q = re.sub(r"^\d+\.\s*", "", q)  # Remove "1. ", "2. ", etc.
    q = re.sub(r"\s*\(Tables:.*?\)\s*$", "", q)  # Remove "(Tables: ...)" at the end
    return q.strip()

def split_questions(raw_text):
    """Split and clean questions if they come in a block of text."""
    raw_questions = re.split(r'\n\d+\.\s+', "\n" + raw_text.strip())
    return [clean_question(q) for q in raw_questions if q.strip()]

def generate_plans():
    try:
        with open("generated_questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        tables = data["tables"]

        # Handle both string and list cases
        raw_questions = data["questions"]
        if isinstance(raw_questions, str):
            questions = split_questions(raw_questions)
        elif isinstance(raw_questions, list):
            questions = [clean_question(q) for q in raw_questions if isinstance(q, str) and q.strip()]
        else:
            raise ValueError("Unsupported format for 'questions'. Must be string or list.")

        output_dir = "question_plans"
        os.makedirs(output_dir, exist_ok=True)

        global_counter = 4901

        for batch_num, batch in enumerate(chunk_list(questions, 20), start=0):  # 20 per batch to avoid token limits
            batch_start_index = global_counter
            print(f"\n🚀 Processing batch {batch_num + 1} (Q{batch_start_index} to Q{batch_start_index + len(batch) - 1})")

            formatted_questions = json.dumps(batch, indent=2)
            prompt = f'''You are a smart SQL planner. Your job is to break down natural language business/tech strategy questions into logical subtasks.

You have access to these structured tables: {', '.join(tables)}.
Each table includes business, tech, leadership, or hiring-related fields, including nested fields like social posts, IT trends, hiring roles, leadership excerpts, etc.

Your task:
For **each question**, decompose it into a JSON object of subtasks to help generate a SQL query step-by-step.

Important:
- Each **subtask must include only the specific table(s)** required to complete **that individual step**.
- Do **not** list all question-related tables inside each subtask — only what's used for that step.
- There should be **no `"tables"` field** in the JSON output before `"subtasks"` and after `"question"`.
- Each question must include **at least 3 subtasks** (minimum) to ensure logical breakdown. There's **no upper limit** if more steps are needed.

Return format (per question):
[
  {{
    "question": "<original question>",
    "subtasks": [
      {{
        "step": 1,
        "task": "Describe what this subtask is doing",
        "table": ["Table1"]
      }},
      {{
        "step": 2,
        "task": "Next subtask description",
        "table": ["Table2"]
      }}
    ]
  }}
]

Questions:
{formatted_questions}
'''

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a SQL planning assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                raw_output = response.choices[0].message.content.strip()

                # Remove markdown if present
                if raw_output.startswith("```json"):
                    raw_output = raw_output.lstrip("```json").rstrip("```").strip()
                elif raw_output.startswith("```"):
                    raw_output = raw_output.lstrip("```").rstrip("```").strip()

                parsed = json.loads(raw_output)

                for i, item in enumerate(parsed):
                    file_name = f"Q{global_counter + i}.json"
                    with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
                        json.dump(item, f, indent=2)

                print(f"✅ Batch {batch_num + 1} complete. Saved {len(parsed)} questions (Q{global_counter} to Q{global_counter + len(parsed) - 1})")
                global_counter += len(parsed)
                sleep(1)  # polite delay

            except Exception as e:
                print(f"❌ Error in batch {batch_num + 1}: {e}")
                continue

    except Exception as e:
        print(f"Failed to generate plans: {e}")

if __name__ == "__main__":
    generate_plans()