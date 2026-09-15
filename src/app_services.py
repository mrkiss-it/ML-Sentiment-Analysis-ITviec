"""Cached read-only services for the Streamlit demo."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.tv4_analysis import load_inference_bundle, predict_review


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@st.cache_data(show_spinner=False)
def load_reviews() -> pd.DataFrame:
    return pd.read_excel(PROJECT_ROOT / "data" / "processed" / "reviews_cleaned.xlsx")


@st.cache_data(show_spinner=False)
def load_csv(relative_path: str) -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / relative_path)


@st.cache_data(show_spinner=False)
def load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


@st.cache_resource(show_spinner="Đang nạp Logistic Regression và TF-IDF…")
def get_inference_bundle() -> dict:
    return load_inference_bundle(PROJECT_ROOT)


def analyze_review(text: str) -> dict:
    return predict_review(get_inference_bundle(), text)
