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
        table_info = response.json()
        schema = table_info.get('schema', [])
        column_names = [col['column'] for col in schema]
        return column_names
    except Exception as e:
        print(f"Error fetching column names for table {table_name}: {e}")
        return []

def get_table_records(table_name: str) -> List[Dict[str, Union[str, int, float]]]:
    try:
        response = requests.get(f"https://refract-ai-test.whiteflower-fba9f868.centralindia.azurecontainerapps.io/db/records/{table_name}")
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching table records for table {table_name}: {e}")
        return []

def get_question(table_names: List[str]) -> str:
    try:
        selected_tables = random.sample(table_names, k=random.choice([3, 4]))

        all_columns = []
        all_records = []

        for table_name in selected_tables:
            columns = get_column_names(table_name)
            records = get_table_records(table_name)
            all_columns.append(f"Table {table_name}: {columns}")
            all_records.append({table_name: records})

        prompt_input = PROMPT.format(
            table_names=", ".join(selected_tables),
            column_names="\n".join(all_columns)
        )

        question = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_input},
                {"role": "user", "content": f"Using these table records: {all_records}, create 6-8 simple, specific and under 20 words, human-like questions blending context across 2-4 tables, mentioning table names at the end of each question."}
            ]
        )
        # return question.choices[0].message.content
        result = {
            "questions": question.choices[0].message.content,
            "tables": selected_tables,
            "records": all_records
        }

        with open("generated_questions.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print("Questions generated and saved to generated_questions.json\n", question.choices[0].message.content)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

if __name__ == "__main__":
    question = get_question(TABLE_NAMES)
    print(question)
