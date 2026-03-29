import os
import joblib
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from core.reasoning.ltr import trainer
from core.reasoning.ltr.feature_extractor import FEATURE_NAMES


def _build_split(df: pd.DataFrame):
    df = df.sort_values("query")
    gss = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
    train_idx, val_idx = next(gss.split(df, groups=df["query"].values))
    df_train = df.iloc[train_idx].sort_values("query")
    df_val = df.iloc[val_idx].sort_values("query")
    return df_train, df_val


def evaluate_model(model_path: str, df_val: pd.DataFrame):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = joblib.load(model_path)
    X_val = trainer.compute_features(df_val)
    val_scores = model.predict(pd.DataFrame(X_val, columns=FEATURE_NAMES))
    return trainer.evaluate_ranking_metrics(df_val, val_scores)


def fmt(m: dict) -> str:
    return (
        f"top1={m['top1']:.4f} | recall@5={m['recall@5']:.4f} "
        f"| mrr={m['mrr']:.4f} | queries={m['queries']}"
    )


def main():
    print("Loading dataset...")
    df = pd.read_csv(trainer.DATA_PATH)
    df = trainer.augment_with_hard_negatives(df)
    _, df_val = _build_split(df)

    baseline_model = trainer.MODEL_PATH
    baseline = evaluate_model(baseline_model, df_val)
    print(f"BEFORE  -> {fmt(baseline)}")

    backup_path = baseline_model.replace(".pkl", ".pre_retrain.pkl")
    if os.path.exists(baseline_model):
        joblib.dump(joblib.load(baseline_model), backup_path)
        print(f"Backed up baseline model to: {backup_path}")

    print("Retraining model...")
    trainer.train_model()

    after = evaluate_model(trainer.MODEL_PATH, df_val)
    print(f"AFTER   -> {fmt(after)}")

    print("DELTA")
    print(f"  top1:     {after['top1'] - baseline['top1']:+.4f}")
    print(f"  recall@5: {after['recall@5'] - baseline['recall@5']:+.4f}")
    print(f"  mrr:      {after['mrr'] - baseline['mrr']:+.4f}")


if __name__ == "__main__":
    main()
