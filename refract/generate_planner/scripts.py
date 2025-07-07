import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def generate_plans():
    try:
        with open(r"C:\Work Repos\dev-anikait\generated_questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        questions = data["questions"]
        tables = data["tables"]

        # Prepare prompt
        prompt = f'''You are a smart SQL planner. Your job is to break down natural language business/tech strategy questions into logical subtasks.

You have access to these structured tables: {', '.join(tables)}.
Each table includes business, tech, leadership, or hiring-related fields, including nested fields like social posts, IT trends, hiring roles, leadership excerpts, etc.

Your task:
For **each question**, decompose it into a JSON object of subtasks to help generate a SQL query step-by-step.

Important:
- Each **subtask must include only the specific table(s)** required to complete **that individual step**.
- Do **not** list all question-related tables inside each subtask — only what's used for that step.
- Include a `"tables"` field at the top level with all required tables for the full question.
- Each question must include **at least 3 subtasks** (minimum) to ensure logical breakdown. There's **no upper limit** if more steps are needed.

Return format (per question):

[
  {{
    "question": "<original question>",
    "tables": ["<all tables needed overall>"],
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

Example:

Question:
"Who are the key leaders at New York Life impacting technology investments in data management strategies?"
(Tables: CompanyManagementDetail, CompanyITPartnerDetail, CompanyInfo)

[
  {{
    "question": "Who are the key leaders at New York Life impacting technology investments in data management strategies?",
    "tables": ["CompanyManagementDetail", "CompanyITPartnerDetail", "CompanyInfo"],
    "subtasks": [
      {{
        "step": 1,
        "task": "Identify data management-related IT partnerships for New York Life",
        "table": ["CompanyITPartnerDetail"]
      }},
      {{
        "step": 2,
        "task": "Filter by New York Life's Company ID",
        "table": ["CompanyInfo"]
      }},
      {{
        "step": 3,
        "task": "Identify technology or data-focused leaders at New York Life",
        "table": ["CompanyManagementDetail"]
      }},
      {{
        "step": 4,
        "task": "Match leadership roles with relevant IT/data strategy areas",
        "table": ["CompanyManagementDetail", "CompanyITPartnerDetail"]
      }}
    ]
  }}
]

Questions:
{questions}
'''

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a SQL planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        raw_output = response.choices[0].message.content.strip()

        # Try to clean markdown formatting like triple backticks
        if raw_output.startswith("```json"):
            raw_output = raw_output.lstrip("```json").rstrip("```").strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output.lstrip("```").rstrip("```").strip()

        # Convert text response to JSON object
        parsed = json.loads(raw_output)

        # Save to file
        with open("sql_planning_output.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        # Print individual steps
        for question_obj in parsed:
            print(f"\nQuestion: {question_obj['question']}")
            for subtask in question_obj["subtasks"]:
                print(f"Step {subtask['step']}: {subtask['task']}")

    except Exception as e:
        print(f"Failed to generate plans: {e}")

if __name__ == "__main__":
    generate_plans()
