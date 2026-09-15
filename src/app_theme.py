"""Visual system shared by the Streamlit ML demo."""

from __future__ import annotations

from html import escape

import altair as alt
import streamlit as st


SENTIMENT_COLORS = {
    "Positive": "#50e3a4",
    "Neutral": "#f4d35e",
    "Negative": "#ff6677",
}


def apply_app_style() -> None:
    """Apply a compact developer-dashboard skin around native widgets."""
    st.html(
        """
        <style>
        :root {
          --ml-bg: #080b10;
          --ml-surface: rgba(18, 24, 34, .82);
          --ml-surface-strong: #141b26;
          --ml-surface-soft: rgba(255, 255, 255, .035);
          --ml-border: rgba(255, 255, 255, .085);
          --ml-border-hover: rgba(255, 255, 255, .16);
          --ml-text: #f1f5f9;
          --ml-muted: #9eabba;
          --ml-blue: #7aa7ff;
          --ml-mint: #50e3a4;
          --ml-yellow: #f4d35e;
          --ml-orange: #ff994f;
          --ml-red: #ff6677;
          --ml-radius-sm: 11px;
          --ml-radius-md: 15px;
          --ml-radius-lg: 18px;
          --ml-font: "DM Sans", system-ui, sans-serif;
          --ml-mono: "JetBrains Mono", ui-monospace, monospace;
        }

        html, body, [data-testid="stAppViewContainer"] { font-family: var(--ml-font); }
        [data-testid="stMainBlockContainer"] {
          width: 100%; max-width: 1680px; margin-inline: auto;
          padding: 4.6rem clamp(1.15rem, 2.8vw, 3.5rem) 2rem;
        }
        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(circle at 82% -10%, rgba(122, 167, 255, .10), transparent 31rem),
            radial-gradient(circle at 5% 105%, rgba(80, 227, 164, .05), transparent 28rem),
            var(--ml-bg);
        }
        header[data-testid="stHeader"] {
          background: rgba(8, 11, 16, .76); backdrop-filter: blur(10px);
        }

        section[data-testid="stSidebar"] {
          background:
            radial-gradient(circle at 10% 0%, rgba(122, 167, 255, .11), transparent 14rem),
            #0c1017;
          border-right: 1px solid var(--ml-border);
          box-shadow: 10px 0 32px rgba(0, 0, 0, .14);
        }
        [data-testid="stSidebarHeader"] {
          min-height: 80px; padding-inline: 1.15rem;
          border-bottom: 1px solid rgba(255, 255, 255, .055);
        }
        [data-testid="stSidebarHeader"] > div:first-child { width: 218px !important; flex: 0 0 218px; }
        [data-testid="stSidebarLogo"] {
          width: 218px !important; max-width: 100% !important;
          height: auto !important; max-height: 54px !important; object-fit: contain;
        }
        [data-testid="stSidebarNav"] { padding: .5rem .4rem .35rem; }
        [data-testid="stSidebarNavSeparator"] { border-color: var(--ml-border); }
        [data-testid="stSidebarContent"] { display: flex; flex-direction: column; min-height: 100%; }
        [data-testid="stNavSectionHeader"] {
          margin: .75rem .45rem .35rem; color: #728096;
          font: 600 .67rem var(--ml-mono); letter-spacing: .1em; text-transform: uppercase;
        }
        [data-testid="stSidebarNavLink"] {
          min-height: 43px; margin-block: 3px; padding-inline: .75rem;
          border: 1px solid transparent; border-radius: var(--ml-radius-sm);
          color: #aab5c5; transition: 140ms ease;
        }
        [data-testid="stSidebarNavLink"] p { font-size: .94rem; font-weight: 500; }
        [data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] { color: #748196; }
        [data-testid="stSidebarNavLink"]:hover {
          transform: translateX(2px); color: var(--ml-text);
          background: rgba(122, 167, 255, .06); border-color: var(--ml-border);
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] {
          color: var(--ml-text); background: rgba(122, 167, 255, .12);
          border-color: rgba(122, 167, 255, .25);
          box-shadow: inset 3px 0 0 var(--ml-blue), 0 7px 18px rgba(0, 0, 0, .12);
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] p { font-weight: 700; }
        [data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stIconMaterial"] { color: var(--ml-blue); }
        [data-testid="stSidebarUserContent"] { margin-top: auto; padding: 1.2rem .4rem 1rem; }
        .st-key-sidebar_status {
          position: relative; overflow: hidden; padding: .35rem;
          border-color: rgba(122, 167, 255, .16) !important;
          background: rgba(17, 23, 33, .88) !important;
        }
        .st-key-sidebar_status::before {
          content: ""; position: absolute; top: 0; left: 17px; width: 44px; height: 2px;
          background: linear-gradient(90deg, var(--ml-blue), var(--ml-mint));
        }
        .st-key-sidebar_status [data-testid="stCaptionContainer"] p {
          color: #7f9fd8; font: 600 .7rem var(--ml-mono); letter-spacing: .08em;
        }
        .st-key-sidebar_status [data-testid="stMetric"] {
          min-height: 74px; padding: .65rem .7rem; background: rgba(7, 10, 16, .58);
        }
        .st-key-sidebar_status [data-testid="stMetricValue"] { font-size: 1.22rem; }

        [data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
          border: 1px solid var(--ml-border); background: var(--ml-surface);
          box-shadow: 0 12px 32px rgba(0, 0, 0, .15);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
          border-radius: var(--ml-radius-lg); transition: border-color 150ms ease, box-shadow 150ms ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
          border-color: var(--ml-border-hover); box-shadow: 0 15px 36px rgba(0, 0, 0, .19);
        }
        [data-testid="stMetric"] {
          min-height: 112px; padding: .95rem 1.1rem; border-radius: var(--ml-radius-md);
          transition: transform 150ms ease, border-color 150ms ease;
        }
        [data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: rgba(122, 167, 255, .25); }
        /* Native bordered metrics have their own inner padding: use one layer. */
        [data-testid="stMetric"] > div { padding: 0; border: 0; }
        [data-testid="stMetricValue"] p { margin: 0; }
        [data-testid="stMetricValue"], [data-testid="stMetricDelta"], [data-testid="stBadge"], code, pre {
          font-family: var(--ml-mono);
        }
        [data-testid="stMetricLabel"] { color: var(--ml-muted); font-size: .9rem; }
        [data-testid="stMetricValue"] {
          color: var(--metric-accent, var(--ml-blue));
          font-size: clamp(1.65rem, 2vw, 2.35rem); letter-spacing: -.045em;
        }
        :is(.st-key-kpi_positive) { --metric-accent: var(--ml-mint); }
        :is(.st-key-kpi_neutral) { --metric-accent: var(--ml-yellow); }
        :is(.st-key-kpi_negative, .st-key-kpi_error) { --metric-accent: var(--ml-red); }
        :is(.st-key-kpi_speed) { --metric-accent: var(--ml-orange); }

        h1, h2, h3 { color: var(--ml-text); letter-spacing: -.03em; }
        h1 { font-size: clamp(2.25rem, 2.6vw, 3rem); text-wrap: balance; }
        h2 { font-size: 1.62rem; } h3 { font-size: 1.25rem; }
        p { line-height: 1.55; }
        :is(h2, h3, h4) [data-testid="stIconMaterial"] { color: var(--ml-blue); }
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--ml-muted); opacity: 1; }

        .st-key-page_header { margin-bottom: .65rem; }
        .st-key-page_header [data-testid="stCaptionContainer"] p {
          color: #7ea1de; font: 600 .74rem var(--ml-mono); letter-spacing: .11em;
        }
        .st-key-page_header h1 { margin: -.15rem 0 .1rem; }
        .st-key-page_header h1 { padding-block: .2rem .45rem; }
        .st-key-page_header [data-testid="stMarkdownContainer"] > p { max-width: 960px; }

        .ml-section-label {
          display: flex; align-items: center; gap: .65rem; margin: .4rem 0 .2rem;
          color: #7f8da1; font: 600 .74rem var(--ml-mono); letter-spacing: .1em; text-transform: uppercase;
        }
        .ml-section-label::after { content: ""; height: 1px; flex: 1; background: var(--ml-border); }
        .ml-hero-note {
          padding: .85rem 1rem; border: 1px solid rgba(122, 167, 255, .18);
          border-radius: var(--ml-radius-sm); background: rgba(122, 167, 255, .055);
          color: #b8c6d9; font-size: .96rem;
        }
        .ml-step {
          display: flex; gap: .9rem; align-items: flex-start; padding: .76rem 0;
          border-bottom: 1px solid rgba(255,255,255,.06);
        }
        .ml-step:last-child { border-bottom: 0; }
        .ml-step-index {
          display: grid; place-items: center; flex: 0 0 30px; height: 30px;
          border: 1px solid rgba(122,167,255,.28); border-radius: 9px;
          color: var(--ml-blue); background: rgba(122,167,255,.08); font: 600 .7rem var(--ml-mono);
        }
        .ml-step strong { display: block; color: #e7edf6; margin-bottom: .12rem; }
        .ml-step span { color: var(--ml-muted); font-size: .93rem; }
        .ml-result {
          padding: 1.25rem 1.35rem; border-radius: var(--ml-radius-md);
          border: 1px solid color-mix(in srgb, var(--result-color) 30%, transparent);
          background: color-mix(in srgb, var(--result-color) 8%, transparent);
        }
        .ml-result-label { color: var(--result-color); font: 700 .8rem var(--ml-mono); letter-spacing: .1em; }
        .ml-result-value { color: #f7f9fc; font-size: clamp(2rem, 4vw, 3.5rem); font-weight: 700; letter-spacing: -.06em; }
        .ml-result-sub { color: var(--ml-muted); font-size: .96rem; }
        .ml-review-quote {
          margin-top: .5rem; padding: 1rem 1.1rem; border-left: 2px solid var(--ml-blue);
          border-radius: 0 11px 11px 0; background: rgba(122,167,255,.045); color: #c8d1df;
        }
        .ml-empty-result {
          min-height: 328px; display: flex; flex-direction: column; justify-content: center;
          align-items: center; text-align: center; padding: 2rem;
          border: 1px dashed rgba(122,167,255,.22); border-radius: 14px;
          background: radial-gradient(ellipse at center, rgba(122,167,255,.065), transparent 75%);
        }
        .ml-empty-symbol { color: var(--ml-blue); font: 500 2.6rem var(--ml-mono); margin-bottom: 1rem; }
        .ml-empty-result h3 { margin: 0 0 .5rem; }
        .ml-empty-result p { color: var(--ml-muted); max-width: 300px; }

        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
          border-color: var(--ml-border); border-radius: var(--ml-radius-sm);
          background: rgba(6, 9, 14, .68); transition: 140ms ease;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
        [data-testid="stTextArea"] textarea:focus, [data-testid="stTextInput"] input:focus {
          border-color: rgba(122,167,255,.5); box-shadow: 0 0 0 3px rgba(122,167,255,.08);
        }
        [data-testid="stButtonGroup"] [role="toolbar"], [data-testid="stButtonGroup"] [role="radiogroup"] {
          gap: .24rem; padding: .25rem; border: 1px solid var(--ml-border);
          border-radius: var(--ml-radius-sm); background: rgba(5,8,13,.62);
        }
        [data-testid="stButtonGroup"] button { min-height: 40px; border-radius: 8px !important; }
        [data-testid="stButtonGroup"] button p,
        [data-testid="stButton"] button p,
        [data-testid="stFormSubmitButton"] button p,
        [data-testid="stWidgetLabel"] p { font-size: .94rem; }
        [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
          min-height: 42px; border: 1px solid rgba(122,167,255,.34); border-radius: var(--ml-radius-sm);
          color: #08101d; background: var(--ml-blue); font-weight: 700;
          box-shadow: 0 7px 18px rgba(56,92,154,.17); transition: 140ms ease;
        }
        [data-testid="stBaseButton-primary"]:hover, [data-testid="stFormSubmitButton"] button:hover {
          transform: translateY(-1px); filter: brightness(1.05);
        }
        button:focus-visible, a:focus-visible { outline: 2px solid var(--ml-blue); outline-offset: 3px; }
        [data-testid="stExpander"] details, [data-testid="stAlert"] {
          border-color: var(--ml-border); border-radius: var(--ml-radius-md); background: var(--ml-surface);
        }
        [data-testid="stDataFrame"] { overflow: hidden; border: 1px solid var(--ml-border); border-radius: var(--ml-radius-md); }

        :is(
          .st-key-overview_pipeline, .st-key-overview_metric_note, .st-key-feature_insights,
          .st-key-feature_evaluation, .st-key-feature_predict, .st-key-insight_filter,
          .st-key-insight_sentiment, .st-key-insight_aspects, .st-key-wordcloud_panel,
          .st-key-keyword_panel, .st-key-benchmark_chart, .st-key-benchmark_table,
          .st-key-eval_matrix, .st-key-eval_class, .st-key-error_filters,
          .st-key-error_detail, .st-key-predict_form, .st-key-predict_status,
          .st-key-probability_panel, .st-key-token_panel, .st-key-pipeline_trace
        ) {
          position: relative; overflow: hidden; border-color: var(--ml-border) !important;
          background: var(--ml-surface); box-shadow: 0 12px 32px rgba(0,0,0,.15);
        }
        :is(
          .st-key-overview_pipeline, .st-key-overview_metric_note, .st-key-feature_insights,
          .st-key-feature_evaluation, .st-key-feature_predict, .st-key-insight_filter,
          .st-key-insight_sentiment, .st-key-insight_aspects, .st-key-wordcloud_panel,
          .st-key-keyword_panel, .st-key-benchmark_chart, .st-key-benchmark_table,
          .st-key-eval_matrix, .st-key-eval_class, .st-key-error_filters,
          .st-key-error_detail, .st-key-predict_form, .st-key-predict_status,
          .st-key-probability_panel, .st-key-token_panel, .st-key-pipeline_trace
        )::before {
          content: ""; position: absolute; z-index: 2; top: 0; left: 18px;
          width: 43px; height: 2px; background: var(--card-accent, var(--ml-blue)); opacity: .78;
        }
        .st-key-feature_insights, .st-key-insight_aspects, .st-key-token_panel { --card-accent: var(--ml-mint); }
        .st-key-feature_evaluation, .st-key-eval_class, .st-key-pipeline_trace { --card-accent: var(--ml-yellow); }
        .st-key-feature_predict, .st-key-wordcloud_panel, .st-key-predict_form { --card-accent: var(--ml-orange); }
        .st-key-error_detail { --card-accent: var(--ml-red); }
        :is(.st-key-feature_insights, .st-key-feature_evaluation, .st-key-feature_predict) {
          min-height: 184px; transition: transform 150ms ease, border-color 150ms ease;
        }
        :is(.st-key-feature_insights, .st-key-feature_evaluation, .st-key-feature_predict):hover {
          transform: translateY(-3px); border-color: color-mix(in srgb, var(--card-accent) 30%, transparent) !important;
        }

        :is(.st-key-overview_metrics, .st-key-insight_metrics, .st-key-eval_metrics, .st-key-predict_metrics)[data-testid="stHorizontalBlock"] {
          display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .9rem;
        }
        :is(.st-key-overview_metrics, .st-key-insight_metrics, .st-key-eval_metrics) [data-testid="stMetric"] { height: 130px; }
        .st-key-predict_metrics[data-testid="stHorizontalBlock"] { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .st-key-predict_metrics [data-testid="stMetric"] { min-height: 106px; }
        .st-key-predict_metrics [data-testid="stMetricValue"] { font-size: 1.72rem; }
        .st-key-benchmark_winner [data-testid="stMetricValue"] { font: 650 clamp(1.05rem, 1.3vw, 1.5rem) var(--ml-font); white-space: normal; }
        .st-key-wordcloud_panel [data-testid="stImage"] { width: 100%; }
        .st-key-wordcloud_panel [data-testid="stImage"] img {
          border-radius: 12px; width: 100%; height: 340px; object-fit: contain;
        }
        @keyframes ml-enter { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
        [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { animation: ml-enter 260ms ease-out both; }
        @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
        @media (max-width: 900px) {
          [data-testid="stMainBlockContainer"] { padding-inline: 1rem; padding-top: 4rem; }
          [data-testid="stMetric"] { min-height: 108px; }
        }
        </style>
        """
    )


def page_header(section: str, title: str, description: str, badges: list[str] | None = None) -> None:
    """Render a consistent page identity and compact evidence badges."""
    with st.container(key="page_header", gap="xsmall"):
        st.caption(f"SENTIMENT ML LAB / {section.upper()}")
        st.title(title)
        st.write(description)
        if badges:
            st.markdown(" ".join(badges))


def section_label(text: str) -> None:
    """Create a quiet divider used to pace information-dense pages."""
    st.html(f'<div class="ml-section-label">{escape(text)}</div>')


@st.cache_data(show_spinner=False, max_entries=16)
def keyword_cloud_svg(frequencies: dict[str, int], sentiment: str) -> str:
    """Lay out exported keyword counts as a crisp, high-contrast web graphic."""
    from wordcloud import WordCloud

    palette = (
        ["#50e3a4", "#91f0c5", "#7aa7ff", "#c8d9ff", "#e5f7ef"]
        if sentiment == "Positive"
        else ["#ff6677", "#ff994f", "#ffc39b", "#f4d35e", "#f5dce0"]
    )

    def color_word(word, font_size, position, orientation, random_state=None, **kwargs):
        return palette[sum(ord(character) for character in word) % len(palette)]

    cloud = WordCloud(
        width=1000, height=470, background_color="#101620",
        max_words=40, min_font_size=14, max_font_size=125,
        prefer_horizontal=1, relative_scaling=.4, margin=12,
        random_state=42, color_func=color_word,
    ).generate_from_frequencies(frequencies)
    return cloud.to_svg(embed_font=True)


def style_chart(chart: alt.Chart) -> alt.Chart:
    """Apply shared typography and quiet chart chrome."""
    return (
        chart.configure(font="DM Sans", background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor="#a0adbf", titleColor="#a0adbf", labelFontSize=14,
            titleFontSize=14, titleFontWeight=500, labelPadding=8, titlePadding=12,
            domain=False, ticks=False, gridColor="#252e3c", gridOpacity=0.5,
        )
        .configure_legend(labelColor="#cbd5e1", titleColor="#a0adbf", labelFontSize=14, titleFontSize=14)
    )
