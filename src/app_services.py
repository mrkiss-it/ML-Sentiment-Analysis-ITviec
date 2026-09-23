"""Cached read-only services for the Streamlit demo."""

from __future__ import annotations

import json
from concurrent.futures import Future
from pathlib import Path
from threading import Thread

import pandas as pd
import streamlit as st

from src.tv4_analysis import load_inference_bundle, predict_review


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@st.cache_data(show_spinner=False)
def load_reviews() -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "data" / "processed" / "reviews_cleaned.csv")


@st.cache_data(show_spinner=False)
def load_csv(relative_path: str) -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / relative_path)


@st.cache_data(show_spinner=False)
def load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


@st.cache_resource(show_spinner=False)
def start_inference_loading() -> Future[dict]:
    """Warm the shared model without blocking the first page render."""
    future: Future[dict] = Future()

    def load() -> None:
        try:
            future.set_result(load_inference_bundle(PROJECT_ROOT, model_dir="models/retrained_v2"))
        except BaseException as error:
            future.set_exception(error)

    Thread(target=load, name="ml-inference-warmup", daemon=True).start()
    return future


def get_inference_bundle() -> dict:
    return start_inference_loading().result()


def analyze_review(text: str) -> dict:
    return predict_review(get_inference_bundle(), text)
