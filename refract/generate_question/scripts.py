import openai
import requests
import random
import json
import os
from typing import List, Dict, Union
from dotenv import load_dotenv
from prompt import PROMPT

load_dotenv()
openai.api_key = os.getenv("OPEN_AI_API_KEY")

TABLE_NAMES = [
    "CompanyInfo", "CompanyDataCenter", "CompanyDealMaster", "CompanyFacebookDetail", "CompanyFocusAreaDetail", "CompanyHiringDetail",
    "CompanyInstagramDetail", "CompanyITPartnerDetail", "CompanyLeadershipExcerpt", "CompanyManagementDetail", "CompanyTechStack",
    "CompanyTwitterDetail", "CompanyVendorProductDetail", "CompanyVendorTechDetail", "CompanyYoutubeDetail", "IndustryBusinessTrend",
    "IndustryITTrend", "LookUpValue", "PageInfo", "PersonaFaceBook", "PersonaInstagramProfile", "PersonaLinkedinActivity",
    "PersonaLinkedinPost", "PersonaLinkedInProfile", "PersonaMisc", "PersonaTwitterProfile", "PersonaTwitterTweets", "PersonaUser",
    "PersonaYoutubeProfile", "SectionData", "SectionInfo", "SectionTitle", "SocialMediaInfo", "PersonaTitle"
]

def get_column_names(table_name: str) -> List[str]:
    try:
        response = requests.get(f"https://refract-ai-test.whiteflower-fba9f868.centralindia.azurecontainerapps.io/db/schema/{table_name}")
        response.raise_for_status()
        schema = response.json().get('schema', [])
        return [col['column'] for col in schema]
    except Exception as e:
        print(f"Error fetching columns for {table_name}: {e}")
        return []

def get_table_records(table_name: str) -> List[Dict[str, Union[str, int, float]]]:
    try:
        response = requests.get(f"https://refract-ai-test.whiteflower-fba9f868.centralindia.azurecontainerapps.io/db/records/{table_name}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching records for {table_name}: {e}")
        return []

def get_question(table_names: List[str]) -> None:
    try:
        selected_tables = random.sample(table_names, k=random.choice([3, 4]))
        all_columns = []
        all_records = []

        for table_name in selected_tables:
            cols = get_column_names(table_name)
            recs = get_table_records(table_name)
            all_columns.append(f"Table {table_name}: {cols}")
            all_records.append({table_name: recs})

        prompt_input = PROMPT.format(
            table_names=", ".join(selected_tables),
            column_names="\n".join(all_columns)
        )

        question_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_input},
                {"role": "user", "content": "Generate the full list of 100 questions as instructed above all at once."}
            ]
        )

        content = question_response.choices[0].message.content
        questions = [line.strip("- ").strip() for line in content.strip().split("\n") if line.strip()]

        result = {
            "questions": questions,
            "tables": selected_tables,
            "records": all_records
        }

        with open("generated_questions.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print("✅ 100 questions generated and saved to generated_questions.json")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_question(TABLE_NAMES)
