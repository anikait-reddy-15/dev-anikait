from fastapi import FastAPI, UploadFile, Form, File
from autogluon.tabular import TabularPredictor
from typing import Optional
import os, json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

app = FastAPI()
BASE_MODEL_DIR = "models"

@app.post("/train")
async def train_model(
    file: UploadFile,
    model_id: str = Form(...),
    target_column: str = Form(...),
    model_purpose: str = Form(...),
    # eval_metric: str = Form("f1"),
    problem_type: str = Form("binary"),
    presets: str = Form("best_quality"),
    time_limit: int = Form(600),
    models_to_use: Optional[str] = Form(None)
):

    if problem_type == "regression":
        eval_metric = "root_mean_squared_error"  # or "r2", "mae", etc.
    elif problem_type == "binary":
        eval_metric = "f1"  # or "accuracy", "roc_auc", etc.
    elif problem_type == "multiclass":
        eval_metric = "accuracy"

    df = pd.read_csv(file.file)
    df.columns = df.columns.str.strip()
    df = df[df[target_column].notnull() & np.isfinite(df[target_column])]

    if df.empty:
        return {"error": "All rows in the dataset had invalid target values."}

    train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

    hyperparameters = json.loads(models_to_use) if models_to_use else None

    model_dir = os.path.join(BASE_MODEL_DIR, model_id)
    predictor_path = os.path.join(model_dir, "predictor")
    os.makedirs(predictor_path, exist_ok=True)

    predictor = TabularPredictor(label=target_column, path=predictor_path,
                                 problem_type=problem_type, eval_metric=eval_metric).fit(
        train_data=train_data,
        presets=presets,
        time_limit=time_limit,
        hyperparameters=hyperparameters
    )

    results = predictor.evaluate(test_data)
    predictions = predictor.predict(test_data)

    leaderboard_df = predictor.leaderboard(test_data, silent=True)
    leaderboard_dict = leaderboard_df.to_dict(orient="records")

    metadata = {
        "target_column": target_column,
        "model_purpose": model_purpose,
        "eval_metric": eval_metric,
        "problem_type": problem_type,
        "presets": presets,
        "time_limit": time_limit,
        "hyperparameters": hyperparameters
    }
    with open(os.path.join(model_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f)

    features = train_data.drop(columns=[target_column]).columns.tolist()
    with open(os.path.join(model_dir, "features.json"), "w") as f:
        json.dump(features, f)

    response = {
        "message": f"Model '{model_id}' and '{models_to_use}' trained and evaluated.",
        "evaluation_results": results,
        "sample_predictions": predictions[:10].tolist(),
        "features": features,
        "leaderboard": leaderboard_dict
    }

    with open(os.path.join(model_dir, "response.json"), "w") as f:
        json.dump(response, f, indent=4)

    return response


