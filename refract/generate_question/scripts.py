import requests
import random
import json
import os
from typing import List, Dict, Union
from dotenv import load_dotenv
from prompt import PROMPT

load_dotenv()

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

        # Construct the prompt
        prompt_input = PROMPT.format(
            table_names=", ".join(selected_tables),
            column_names="\n".join(all_columns)
        )

        # Send to hosted inference API
        api_url = "https://4vemmwmcpb.ap-south-1.awsapprunner.com/structured_output/text"
        payload = json.dumps({
            "params": {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "prompt_template": prompt_input,
                "inputs": {},
                "output_schema": {
                    "questions": {
                        "type": "list",
                        "description": "List of 10 unique business or tech strategy questions"
                    }
                }
            }
        })

        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, headers=headers, data=payload)
        response.raise_for_status()

        result_json = response.json()

        # Parse response: string of questions inside result_json["data"]["questions"]
        questions_text = result_json.get("data", {}).get("questions", "")
        questions_list = [q.strip() for q in questions_text.split("\n") if q.strip()]
        questions_list = [q[q.find(".")+1:].strip() if "." in q else q for q in questions_list]

        if not questions_list or len(questions_list) < 10:
            print("⚠️ Could not extract a valid list of questions from the response.")
            return

        result = {
            "questions": questions_list,
            "tables": selected_tables,
            "records": all_records
        }

        with open("generated_questions.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print("✅ 10 questions generated and saved to generated_questions.json")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    get_question(TABLE_NAMES)