import pandas as pd
import lightgbm as lgb
import joblib
import os
import numpy as np
from core.reasoning.ltr.feature_extractor import VidhiSakhaFeatureExtractor


DATA_PATH = "dataset/ltr_dataset.csv"
MODEL_PATH = "models/ltr_model.pkl"


def train_model():

    print("📖 Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # CRITICAL
    df = df.sort_values("query")

    extractor = VidhiSakhaFeatureExtractor()

    X, y = [], []

    print("⚙️ Extracting features...")

    for _, row in df.iterrows():

        features = extractor.extract(
            row['query'],
            row['article_id'],
            row['article_title'],
            row['neural_score'],
            row['rank']
        )

        X.append(features)
        y.append(row['is_correct'])


    X = np.array(X)
    y = np.array(y)


    groups = df.groupby("query").size().values


    model = lgb.LGBMRanker(

        objective="lambdarank",

        metric="ndcg",

        boosting_type="gbdt",

        n_estimators=300,

        learning_rate=0.05,

        num_leaves=63,

        importance_type="gain"
    )


    print("🏋️ Training LambdaMART...")

    model.fit(X, y, group=groups)


    os.makedirs("models", exist_ok=True)

    joblib.dump(model, MODEL_PATH)


    print("✅ LambdaMART Model Saved")


if __name__ == "__main__":
    train_model()
