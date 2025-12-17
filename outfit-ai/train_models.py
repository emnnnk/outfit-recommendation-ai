import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from config import (
    CATEGORICAL_FEATURES,
    DATA_FILE,
    FEATURE_COLUMNS,
    MODELS_DIR,
    MODEL_PARAMS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    TRAINING_CONFIG,
)
from rules_baseline import rule_based_outfit


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _create_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def _split_data(df: pd.DataFrame, *, test_size: float, val_size: float, seed: int):
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )

    val_ratio_of_trainval = val_size / max(1e-9, (1.0 - test_size))
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval,
        y_trainval,
        test_size=val_ratio_of_trainval,
        random_state=seed,
        stratify=y_trainval,
    )

    return X_train, X_val, X_test, y_train, y_val, y_test


def _evaluate_classifier(
    *,
    name: str,
    pipeline: Optional[Pipeline],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    classes: np.ndarray,
) -> Dict[str, Any]:
    if pipeline is None:
        raise ValueError("pipeline cannot be None")

    y_pred = pipeline.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, average="macro"))
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    return {
        "model": name,
        "accuracy": acc,
        "macro_f1": f1,
        "confusion_matrix": cm.tolist(),
        "classes": classes.tolist(),
    }


def _evaluate_rules(
    *,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    classes: np.ndarray,
) -> Dict[str, Any]:
    y_pred = X_test.apply(
        lambda r: rule_based_outfit(
            int(r["sicaklik"]),
            str(r["yagmur"]),
            str(r["ruzgar"]),
            str(r["ortam"]),
        ),
        axis=1,
    )

    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred, average="macro"))
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    return {
        "model": "rules",
        "accuracy": acc,
        "macro_f1": f1,
        "confusion_matrix": cm.tolist(),
        "classes": classes.tolist(),
    }


def _build_xgb_or_rf_pipeline(preprocessor: ColumnTransformer, *, seed: int) -> Tuple[str, Pipeline]:
    try:
        from xgboost import XGBClassifier  # type: ignore

        clf = XGBClassifier(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=seed,
            n_jobs=-1,
        )
        display_name = "XGBoost"
    except Exception:
        clf = RandomForestClassifier(**MODEL_PARAMS["random_forest"])
        display_name = "RandomForest"

    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", clf),
        ]
    )

    return "xgboost", display_name, pipeline


def _build_mlp_pipeline(preprocessor: ColumnTransformer, *, seed: int) -> Tuple[str, Pipeline]:
    clf = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size="auto",
        learning_rate_init=1e-3,
        max_iter=600,
        early_stopping=False,   # <<< BU SATIR
        n_iter_no_change=20,    # kalsa da olur, etkisiz
        random_state=seed,
    )


    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("scaler", StandardScaler(with_mean=False)),
            ("classifier", clf),
        ]
    )

    return "mlp", pipeline


def _save_pipeline(*, pipeline: Pipeline, filename: str) -> str:
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, filename)
    joblib.dump(pipeline, path)
    return path


def train_all(*, dataset_path: str, test_size: float, val_size: float, seed: int) -> Dict[str, Any]:
    df = pd.read_csv(dataset_path)
    X_train, X_val, X_test, y_train, y_val, y_test = _split_data(
        df, test_size=test_size, val_size=val_size, seed=seed
    )

    classes = np.array(sorted(y_train.unique().tolist()))

    preprocessor = _create_preprocessor()

    xgb_key, xgb_display_name, xgb_pipe = _build_xgb_or_rf_pipeline(preprocessor, seed=seed)
    mlp_name, mlp_pipe = _build_mlp_pipeline(preprocessor, seed=seed)

    xgb_pipe.fit(X_train, y_train)
    mlp_pipe.fit(X_train, y_train)

    metrics_rules = _evaluate_rules(X_test=X_test, y_test=y_test, classes=classes)
    metrics_xgb = _evaluate_classifier(name=xgb_key, pipeline=xgb_pipe, X_test=X_test, y_test=y_test, classes=classes)
    metrics_mlp = _evaluate_classifier(
        name=mlp_name, pipeline=mlp_pipe, X_test=X_test, y_test=y_test, classes=classes
    )

    timestamp = _utc_timestamp()

    files: Dict[str, str] = {}
    files[xgb_key] = _save_pipeline(pipeline=xgb_pipe, filename=f"{xgb_key}_{timestamp}.pkl")
    files[mlp_name] = _save_pipeline(pipeline=mlp_pipe, filename=f"{mlp_name}_{timestamp}.pkl")

    files["xgb_latest"] = _save_pipeline(pipeline=xgb_pipe, filename=f"xgb_model.pkl")
    files["mlp_latest"] = _save_pipeline(pipeline=mlp_pipe, filename=f"mlp_model.pkl")

    metrics_by_model = {
        "rules": metrics_rules,
        xgb_key: metrics_xgb,
        mlp_name: metrics_mlp,
    }

    best_name = max(
        [xgb_key, mlp_name],
        key=lambda k: (metrics_by_model[k]["macro_f1"], metrics_by_model[k]["accuracy"]),
    )

    if best_name == xgb_key:
        best_pipe = xgb_pipe
    else:
        best_pipe = mlp_pipe

    files["best_model"] = _save_pipeline(pipeline=best_pipe, filename="best_model.pkl")

    metrics_payload: Dict[str, Any] = {
        "generated_at_utc": timestamp,
        "dataset_path": dataset_path,
        "splits": {
            "train": int(len(X_train)),
            "val": int(len(X_val)),
            "test": int(len(X_test)),
            "test_size": float(test_size),
            "val_size": float(val_size),
            "random_state": int(seed),
        },
        "best_model": best_name,
        "models": {
            "rules": {**metrics_rules, "model_file": None, "display_name": "Rules"},
            xgb_key: {**metrics_xgb, "model_file": os.path.basename(files["xgb_latest"]), "display_name": xgb_display_name},
            mlp_name: {**metrics_mlp, "model_file": os.path.basename(files["mlp_latest"]), "display_name": "MLP"},
        },
    }

    metrics_path = os.path.join(MODELS_DIR, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=False, indent=2)

    return {
        "metrics_path": metrics_path,
        "model_files": files,
        "metrics": metrics_payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=DATA_FILE)
    parser.add_argument("--test-size", type=float, default=float(TRAINING_CONFIG.get("test_size", 0.2)))
    parser.add_argument("--val-size", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=int(TRAINING_CONFIG.get("random_state", 42)))
    args = parser.parse_args()

    result = train_all(
        dataset_path=args.dataset,
        test_size=args.test_size,
        val_size=args.val_size,
        seed=args.seed,
    )

    best = result["metrics"]["best_model"]
    print("=" * 80)
    print("TRAINING COMPLETE")
    print(f"metrics.json: {result['metrics_path']}")
    print(f"best_model: {best}")
    print("=" * 80)

    for k, v in result["metrics"]["models"].items():
        print(f"{k}: accuracy={v['accuracy']:.4f} macro_f1={v['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
