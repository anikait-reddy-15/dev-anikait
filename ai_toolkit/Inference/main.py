from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from autogluon.tabular import TabularPredictor
import pandas as pd
import numpy as np
import os
import json
import uuid
import re
import traceback


app = FastAPI()

BASE_MODEL_DIR = "models"

def safe_string(s):
    return re.sub(r'[^\w\-]', '_', s)

@app.post("/predict")
async def predict(
    model_id: str = Form(...),
    file: UploadFile = File(...)
):

    model_path = os.path.join(BASE_MODEL_DIR, model_id)
    predictor_path = os.path.join(model_path, "predictor")
    metadata_path = os.path.join(model_path, "metadata.json")
    features_path = os.path.join(model_path, "features.json")
    error_log_path = os.path.join(model_path, "error.log")
    
    try:
        if not all(os.path.exists(p) for p in [predictor_path, metadata_path, features_path]):
            return {"error": f"Model or its configuration not found for model_id: {model_id}"}

        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        with open(features_path, "r") as f:
            features = json.load(f)

        predictor = TabularPredictor.load(predictor_path)

        input_df = pd.read_csv(file.file)
        input_df.columns = input_df.columns.str.strip()

        import numpy as np
        for col in features:
            if col not in input_df.columns:
                input_df[col] = np.nan

        input_features_df = input_df[features]

        predictions = predictor.predict(input_features_df)
        input_df[metadata["target_column"]] = predictions

        hyperparams = metadata.get("hyperparameters", {})
        model_types = list(hyperparams.keys()) if isinstance(hyperparams, dict) else []
        model_summary = safe_string("_".join(model_types)) if model_types else "default"

        output_file = f"predicted_{model_id}_{model_summary}_{uuid.uuid4().hex}.csv"
        output_path = os.path.join(model_path, output_file)
        input_df.to_csv(output_path, index=False)

        return FileResponse(path=output_path, filename=output_file, media_type='text/csv')

    except Exception as e:
        error_message = traceback.format_exc()

        with open(error_log_path, "a") as log_file:
            log_file.write(f"\n--- ERROR ---\n")
            log_file.write(error_message)
            log_file.write("\n")

        return {"error": str(e)}


