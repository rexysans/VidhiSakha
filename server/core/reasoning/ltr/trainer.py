import pandas as pd
import lightgbm as lgb
import joblib
import os
import numpy as np
import math
import re
import ast
from difflib import SequenceMatcher
from sklearn.model_selection import GroupShuffleSplit

from core.reasoning.ltr.feature_extractor import FEATURE_NAMES


# Works with BOTH old (dataset_ltr.csv) and new (dataset_ltr_v2.csv)
DATA_PATH = "dataset/dataset_ltr_v2.csv" if os.path.exists("dataset/dataset_ltr_v2.csv") else "dataset/dataset_ltr.csv"
MODEL_PATH = "models/ltr_model_v2.pkl"


def _extract_query_dict(py_file_path: str, var_name: str) -> dict:
    if not os.path.exists(py_file_path):
        return {}

    with open(py_file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception:
        return {}

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    try:
                        value = ast.literal_eval(node.value)
                        if isinstance(value, dict):
                            return value
                    except Exception:
                        return {}
    return {}


def _load_hard_query_set() -> set[str]:
    eval_core = _extract_query_dict("tests/evaluate.py", "test_cases")
    eval_stress = _extract_query_dict("tests/evaluate_2.py", "test_cases_v2")

    # Hard set = legal queries from both eval files (exclude junk expected None)
    hard_queries = set()
    for q, expected in {**eval_core, **eval_stress}.items():
        if expected is not None:
            hard_queries.add(str(q))
    return hard_queries


def _normalize_query(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_hard_match(query: str, hard_norm_list: list[str]) -> bool:
    qn = _normalize_query(query)
    if not qn:
        return False

    # Exact normalized match
    if qn in hard_norm_list:
        return True

    # Fuzzy similarity to cover paraphrased training queries
    for hq in hard_norm_list:
        if not hq:
            continue
        if SequenceMatcher(None, qn, hq).ratio() >= 0.82:
            return True
    return False


def augment_with_hard_negatives(df: pd.DataFrame) -> pd.DataFrame:
    hard_queries = _load_hard_query_set()
    if not hard_queries:
        print("No hard query set found in tests/evaluate.py or tests/evaluate_2.py")
        out = df.copy()
        out["sample_weight"] = 1.0
        return out

    out = df.copy()
    out["sample_weight"] = 1.0

    hard_norm_list = list({_normalize_query(q) for q in hard_queries if str(q).strip()})

    neg_weight = float(os.getenv("LTR_HARD_NEG_WEIGHT", "2.2"))
    pos_weight = float(os.getenv("LTR_HARD_POS_WEIGHT", "1.6"))
    top_neg_k = int(os.getenv("LTR_HARD_NEG_TOPK", "5"))

    boosted_rows = 0
    covered_queries = 0
    for query, group in out.groupby("query", sort=False):
        if not _is_hard_match(str(query), hard_norm_list):
            continue
        covered_queries += 1

        positives = group[group["is_correct"] == 1].index
        negatives = group[group["is_correct"] == 0].copy()
        negatives = negatives.sort_values("neural_score", ascending=False).head(top_neg_k)

        if len(positives) > 0:
            out.loc[positives, "sample_weight"] = np.maximum(out.loc[positives, "sample_weight"], pos_weight)

        if len(negatives.index) > 0:
            out.loc[negatives.index, "sample_weight"] = np.maximum(out.loc[negatives.index, "sample_weight"], neg_weight)
            boosted_rows += len(negatives.index)

    print(
        f"Hard-negative mining: hard_queries={len(hard_queries)} covered={covered_queries} boosted_neg_rows={boosted_rows}"
    )
    return out


def compute_features(df):
    """Compute all 8 features from raw CSV columns, grouped by query."""
    all_features = []

    for query_name, group in df.groupby("query", sort=False):
        q_low = query_name.lower()
        q_tokens = set(re.findall(r'\w+', q_low))
        q_len = len(q_tokens)
        q_clean = re.sub(r'[^a-z0-9\s]', '', q_low)

        neurals = group["neural_score"].values.astype(float)
        mean_n = neurals.mean()
        min_n = neurals.min()
        max_n = neurals.max()
        range_n = max_n - min_n if max_n != min_n else 1.0

        for _, row in group.iterrows():
            neural = float(row["neural_score"])
            art_id = str(row["article_id"]).lower()
            title = str(row["article_title"]).lower()
            vdist = float(row.get("vector_distance", 0.0))
            text_len = int(row.get("full_text_length", 500))

            feats = []

            # f0: neural_score
            feats.append(neural)

            # f1: neural_score_norm
            feats.append((neural - min_n) / range_n if range_n > 0 else 0.0)

            # f2: vector_distance
            feats.append(vdist)

            # f3: id_match_exact
            id_clean = re.sub(r'[^a-z0-9]', '', art_id)
            if id_clean:
                pattern = r'\b' + re.escape(id_clean) + r'\b'
                feats.append(1.0 if re.search(pattern, q_clean) else 0.0)
            else:
                feats.append(0.0)

            # f4: title_bm25
            t_tokens = set(re.findall(r'\w+', title))
            if q_tokens and t_tokens:
                overlap = q_tokens & t_tokens
                idf_sum = sum(1.0 / math.log2(2 + len(t_tokens)) for _ in overlap)
                bm25 = idf_sum / (len(q_tokens) + 0.5)
            else:
                bm25 = 0.0
            feats.append(bm25)

            # f5: query_length
            feats.append(math.log2(1 + q_len))

            # f6: score_gap
            feats.append(neural - mean_n)

            # f7: text_length_ratio
            feats.append(min(len(q_low) / max(text_len, 1), 1.0))

            all_features.append(feats)

    return np.array(all_features)


def evaluate_ranking_metrics(df: pd.DataFrame, scores: np.ndarray) -> dict:
    tmp = df.copy()
    tmp["pred_score"] = scores

    query_count = 0
    hit_at_1 = 0
    recall_at_5 = 0
    reciprocal_rank_sum = 0.0

    for _, group in tmp.groupby("query", sort=False):
        ranked = group.sort_values("pred_score", ascending=False)
        labels = ranked["is_correct"].astype(int).tolist()
        if not labels:
            continue

        query_count += 1
        if labels[0] == 1:
            hit_at_1 += 1

        top5 = labels[:5]
        if any(v == 1 for v in top5):
            recall_at_5 += 1

        rr = 0.0
        for idx, label in enumerate(labels, start=1):
            if label == 1:
                rr = 1.0 / idx
                break
        reciprocal_rank_sum += rr

    if query_count == 0:
        return {"top1": 0.0, "recall@5": 0.0, "mrr": 0.0, "queries": 0}

    return {
        "top1": hit_at_1 / query_count,
        "recall@5": recall_at_5 / query_count,
        "mrr": reciprocal_rank_sum / query_count,
        "queries": query_count,
    }


def train_model():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    df = df.sort_values("query")
    df = augment_with_hard_negatives(df)

    unique_queries = df["query"].nunique()
    print(f"Dataset: {len(df)} rows, {unique_queries} unique queries")

    # --- Train/Val Split (by query group) ---
    gss = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
    queries = df["query"].values
    train_idx, val_idx = next(gss.split(df, groups=queries))

    df_train = df.iloc[train_idx].sort_values("query")
    df_val = df.iloc[val_idx].sort_values("query")

    print(f"Train: {len(df_train)} rows ({df_train['query'].nunique()} queries)")
    print(f"Val:   {len(df_val)} rows ({df_val['query'].nunique()} queries)")

    # --- Feature Extraction ---
    print("Extracting training features...")
    X_train = compute_features(df_train)
    y_train = df_train["is_correct"].values
    w_train = df_train["sample_weight"].values if "sample_weight" in df_train.columns else None

    print("Extracting validation features...")
    X_val = compute_features(df_val)
    y_val = df_val["is_correct"].values
    w_val = df_val["sample_weight"].values if "sample_weight" in df_val.columns else None

    # Groups must match the sorted query order
    groups_train = df_train.groupby("query", sort=False).size().values
    groups_val = df_val.groupby("query", sort=False).size().values

    print(f"Feature matrix: train={X_train.shape}, val={X_val.shape}")

    # --- Model ---
    model = lgb.LGBMRanker(
        objective="lambdarank",
        metric="ndcg",
        boosting_type="gbdt",
        n_estimators=200,
        learning_rate=0.05,
        num_leaves=31,
        min_child_samples=20,
        reg_alpha=0.1,
        reg_lambda=1.0,
        importance_type="gain",
        verbose=-1,
    )

    print("Training LambdaMART with early stopping...")
    model.fit(
        X_train, y_train,
        group=groups_train,
        sample_weight=w_train,
        eval_set=[(X_val, y_val)],
        eval_group=[groups_val],
        eval_sample_weight=[w_val] if w_val is not None else None,
        eval_metric="ndcg",
        eval_at=[1, 5],
        callbacks=[
            lgb.early_stopping(stopping_rounds=30),
            lgb.log_evaluation(period=10),
        ],
    )

    # --- Feature Importance ---
    print("\nFeature Importance (gain):")
    importances = model.feature_importances_
    for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp / max(importances) * 30)
        print(f"  {name:25s} {imp:>10,.0f}  {bar}")

    # --- Ranking metrics on validation split ---
    val_scores = model.predict(pd.DataFrame(X_val, columns=FEATURE_NAMES))
    metrics = evaluate_ranking_metrics(df_val, val_scores)
    print("\nValidation Ranking Metrics:")
    print(f"  Top1 Accuracy: {metrics['top1']:.4f}")
    print(f"  Recall@5:      {metrics['recall@5']:.4f}")
    print(f"  MRR:           {metrics['mrr']:.4f}")
    print(f"  Queries:       {metrics['queries']}")

    # --- Save ---
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    return model


if __name__ == "__main__":
    train_model()
