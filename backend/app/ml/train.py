from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
)
from sklearn.model_selection import PredefinedSplit, RandomizedSearchCV
from sklearn.pipeline import Pipeline

from app.ml.data_loader import load_matches
from app.ml.features import LABEL_TO_RESULT, ROLLING_WINDOW, build_feature_matrix, get_feature_columns

MODELS_DIR = Path(__file__).resolve().parents[2] / "data" / "models"
MODEL_PATH = MODELS_DIR / "rf_match_predictor.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

TRAIN_SEASONS = ("15-16", "16-17", "17-18", "18-19", "19-20", "20-21", "21-22")
VAL_SEASONS = ("22-23", "23-24")
TEST_SEASONS = ("24-25",)

PARAM_DISTRIBUTIONS = {
    "classifier__n_estimators": [200, 300, 500],
    "classifier__max_depth": [10, 15, 20, None],
    "classifier__min_samples_leaf": [1, 2, 4, 8],
    "classifier__max_features": ["sqrt", "log2"],
}


def _season_mask(matches: pd.DataFrame, seasons: tuple[str, ...]) -> pd.Series:
    return matches["season"].isin(seasons)


def _build_pipeline(feature_columns: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                SimpleImputer(strategy="median"),
                feature_columns,
            )
        ],
        remainder="drop",
    )
    classifier = RandomForestClassifier(
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def _bookmaker_baseline(y_true: np.ndarray, odds_home, odds_draw, odds_away) -> float:
    predictions = []
    for h, d, a in zip(odds_home, odds_draw, odds_away, strict=True):
        if pd.isna(h) or pd.isna(d) or pd.isna(a):
            predictions.append(0)
            continue
        odds = [h, d, a]
        predictions.append(int(np.argmin(odds)))
    return accuracy_score(y_true, predictions)


def _always_home_baseline(y_true: np.ndarray) -> float:
    predictions = np.zeros_like(y_true)
    return accuracy_score(y_true, predictions)


def evaluate_model(
    pipeline: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    matches_subset: pd.DataFrame,
) -> dict:
    y_pred = pipeline.predict(X)
    y_proba = pipeline.predict_proba(X)

    metrics = {
        "accuracy": float(accuracy_score(y, y_pred)),
        "log_loss": float(log_loss(y, y_proba)),
        "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
        "classification_report": classification_report(
            y, y_pred, target_names=["H", "D", "A"], output_dict=True
        ),
        "baseline_always_home": float(_always_home_baseline(y.to_numpy())),
        "baseline_bookmaker": float(
            _bookmaker_baseline(
                y.to_numpy(),
                matches_subset["AvgH"],
                matches_subset["AvgD"],
                matches_subset["AvgA"],
            )
        ),
    }
    return metrics


def train_and_save() -> dict:
    matches = load_matches()
    X, y = build_feature_matrix(matches)
    feature_columns = get_feature_columns()

    train_mask = _season_mask(matches, TRAIN_SEASONS)
    val_mask = _season_mask(matches, VAL_SEASONS)
    test_mask = _season_mask(matches, TEST_SEASONS)

    X_val, y_val = X[val_mask], y[val_mask]
    X_test, y_test = X[test_mask], y[test_mask]

    fit_mask = train_mask | val_mask
    X_fit = X[fit_mask]
    y_fit = y[fit_mask]
    fit_train_mask = train_mask[fit_mask]
    fit_val_mask = val_mask[fit_mask]

    pipeline = _build_pipeline(feature_columns)

    test_fold = -np.ones(len(X_fit), dtype=int)
    test_fold[fit_val_mask.to_numpy()] = 0

    cv_split = PredefinedSplit(test_fold)

    search = RandomizedSearchCV(
        pipeline,
        param_distributions=PARAM_DISTRIBUTIONS,
        n_iter=20,
        scoring="neg_log_loss",
        cv=cv_split,
        random_state=42,
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_fit, y_fit)

    best_pipeline = search.best_estimator_

    val_matches = matches[val_mask]
    test_matches = matches[test_mask]

    val_metrics = evaluate_model(best_pipeline, X_val, y_val, val_matches)
    test_metrics = evaluate_model(best_pipeline, X_test, y_test, test_matches)

    importances = best_pipeline.named_steps["classifier"].feature_importances_
    feature_importance = sorted(
        zip(feature_columns, importances.tolist(), strict=True),
        key=lambda item: item[1],
        reverse=True,
    )[:15]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)

    metadata = {
        "feature_columns": feature_columns,
        "rolling_window": ROLLING_WINDOW,
        "train_seasons": list(TRAIN_SEASONS),
        "val_seasons": list(VAL_SEASONS),
        "test_seasons": list(TEST_SEASONS),
        "best_params": search.best_params_,
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "top_feature_importances": [
            {"feature": name, "importance": score} for name, score in feature_importance
        ],
        "label_mapping": LABEL_TO_RESULT,
    }

    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    return metadata


def load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run scripts/train_model.py first."
        )
    return joblib.load(MODEL_PATH)


def load_metadata() -> dict:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata not found at {METADATA_PATH}. Run scripts/train_model.py first."
        )
    return json.loads(METADATA_PATH.read_text())
