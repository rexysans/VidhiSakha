import pandas as pd
import numpy as np
import joblib
import os
from core.reasoning.ltr.feature_extractor import VidhiSakhaFeatureExtractor
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

def calibrate_threshold():
    if not os.path.exists("dataset/dataset_ltr.csv"):
        print("❌ Error: dataset_ltr.csv not found.")
        return

    # 1. Load data and artifacts
    print("📖 Loading dataset and model...")
    df = pd.read_csv("dataset/dataset_ltr.csv")
    model = joblib.load("models/ltr_model.pkl")
  
    extractor = VidhiSakhaFeatureExtractor()
    
    # 2. Extract features (Mirroring trainer.py logic)
    print(f"⚙️ Computing features for {len(df)} rows...")
    X = []
    y_true = df['is_correct'].values
    
    for _, row in df.iterrows():
        features = extractor.extract(
            query=row['query'],
            article_id=row['article_id'],
            title=row['article_title'],
            neural_score=row['neural_score'],
            rank=row['rank']
        )
        X.append(features)
    
    X = np.array(X)
    

    y_probs = model.predict(X)

    # 4. Calculate Precision-Recall Tradeoff
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
    
    # 5. Find the "Sweet Spot" (Max F1-Score)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    # Thresholds array is one shorter than precision/recall
    best_threshold = thresholds[min(best_idx, len(thresholds)-1)]
    
    print(f"\n🎯 Optimal Threshold (Max F1): {best_threshold:.4f}")
    print(f"📊 Precision at this point: {precisions[best_idx]:.4f}")
    print(f"📉 Recall at this point: {recalls[best_idx]:.4f}")

    # 6. Recommendation logic
    print("\n💡 Recommendation for VidhiSakhā:")
    if best_threshold > 0.8:
        print("   - Your model is very confident. Use a high threshold (0.9+) to kill all junk.")
    else:
        print("   - Your model is conservative. A threshold around 0.5-0.7 is safer.")

if __name__ == "__main__":
    calibrate_threshold()