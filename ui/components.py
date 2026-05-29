import html
from typing import Iterable

import streamlit as st


def H(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def page_header(title: str, subtitle: str, eyebrow: str = "Workspace") -> None:
    H(
        f"""
        <main class="shell">
            <section class="page-header">
                <div>
                    <p class="eyebrow">{esc(eyebrow)}</p>
                    <h1>{esc(title)}</h1>
                    <p>{esc(subtitle)}</p>
                </div>
            </section>
        """
    )


def close_shell() -> None:
    H("</main>")


def metric_card(label: str, value: str, detail: str = "", tone: str = "blue") -> None:
    H(
        f"""
        <div class="metric-card tone-{esc(tone)}">
            <span>{esc(label)}</span>
            <strong>{esc(value)}</strong>
            <small>{esc(detail)}</small>
        </div>
        """
    )


def section_title(title: str, subtitle: str = "") -> None:
    H(
        f"""
        <div class="section-title">
            <h2>{esc(title)}</h2>
            <p>{esc(subtitle)}</p>
        </div>
        """
    )


def card_start(class_name: str = "") -> None:
    H(f'<section class="panel {esc(class_name)}">')


def card_end() -> None:
    H("</section>")


def chip_row(items: Iterable[str], tone: str = "neutral", empty: str = "No data available") -> None:
    values = [esc(item).title() for item in items if item]
    if not values:
        H(f'<p class="muted">{esc(empty)}</p>')
        return
    chips = "".join(f'<span class="chip chip-{esc(tone)}">{item}</span>' for item in values)
    H(f'<div class="chip-row">{chips}</div>')


def progress_row(label: str, value: float, tone: str = "blue") -> None:
    safe_value = max(0, min(100, float(value or 0)))
    H(
        f"""
        <div class="progress-row">
            <div><span>{esc(label)}</span><strong>{safe_value:.0f}%</strong></div>
            <div class="progress-track"><i class="tone-{esc(tone)}" style="width:{safe_value:.0f}%"></i></div>
        </div>
        """
    )


def insight_row(title: str, body: str, tag: str = "Action") -> None:
    H(
        f"""
        <div class="insight-row">
            <div>
                <strong>{esc(title)}</strong>
                <p>{esc(body)}</p>
            </div>
            <span>{esc(tag)}</span>
        </div>
        """
    )


def empty_state(title: str, body: str, action_label: str = "", page: str = "") -> None:
    H(
        f"""
        <div class="empty-state">
            <strong>{esc(title)}</strong>
            <p>{esc(body)}</p>
        </div>
        """
    )
    if action_label and page and st.button(action_label, type="primary"):
        st.session_state.page = page
        st.rerun()
