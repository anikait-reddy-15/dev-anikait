import openai 
import json
import os

openai.api_key = os.getenv("OPEN_AI_API_KEY")

def generate_answers():
    try:
        with open(r"C:\Users\ASUS\Documents\Work Repositories\dev-soumyajit\refract\generate_question\generated_questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        questions = data["questions"]
        tables = data["tables"]
        records = data["records"]

        prompt = f"""

## Context:
You have access to structured tables containing nested fields like Personas, Org Hierarchies, Technology Investments, Business Priorities, Events, Articles, Speeches, Pitches, Deals, Tech Stacks, IT Budgets, and Communication guidelines.
Each record can have detailed information on individuals, organizations, technologies, or business activities.
You are a contextual answering agent. Based on the following data extracted from tables {', '.join(tables)}, answer each question accurately using only the data provided.

Questions:
{questions}

Table Records:
{records}

Format:
1. <Question>
Answer: <Contextual answer>
"""

        answer = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "create simple, human-like, specific and under 80 words answer for each of the questions based only on the table records provided."}
            ]
        )
        print(answer.choices[0].message.content)

    except Exception as e:
        print(f"Failed to generate answers: {e}")

if __name__ == "__main__":
    generate_answers()
