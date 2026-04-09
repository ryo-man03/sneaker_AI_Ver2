# file: app/services/intelligence.py
from __future__ import annotations

import csv
from io import StringIO
from collections.abc import Sequence
from typing import Final, TypedDict
from urllib.parse import urlparse

from app.core.settings import settings
from app.models.market import MarketSnapshot
from app.models.sneaker import Sneaker
from app.models.stock import StockSnapshot

_CULTURE_LABELS: Final[tuple[str, ...]] = (
    "希少性",
    "ストリート",
    "SNS",
    "コラボ",
    "ブランド",
    "アスリート",
    "テック",
    "ヴィンテージ",
    "流動性",
    "モメンタム",
    "スタイル",
    "文化遺産",
    "デザイン",
    "素材",
    "限定性",
)


class BuyScoreParts(TypedDict):
    market_momentum: int
    liquidity: int
    stock_correlation: int
    culture_signal: int
    risk_penalty: int


class IntakePreview(TypedDict):
    sku: str
    model: str
    hint: str


class CorrelationPoint(TypedDict):
    ticker: str
    company: str
    correlation: float
    relation: str
    change_pct: float
    index_change_pct: float


def ai_available() -> bool:
    return bool(settings.resolved_google_api_key)


def build_culture_vector(sneaker: Sneaker) -> list[tuple[str, float]]:
    brand_bias = {
        "NIKE": 0.05,
        "ADIDAS": 0.02,
        "NEW BALANCE": 0.03,
        "ASICS": 0.01,
    }.get(sneaker.brand.upper(), 0.0)
    base = max(0.28, min(0.95, sneaker.buy_score / 100.0))

    vector: list[tuple[str, float]] = []
    for index, label in enumerate(_CULTURE_LABELS):
        ring_offset = ((index % 5) - 2) * 0.035
        trend_bias = 0.025 if index % 3 == 0 else (-0.015 if index % 4 == 0 else 0.0)
        value = max(0.1, min(0.99, base + brand_bias + ring_offset + trend_bias))
        vector.append((label, round(value, 3)))
    return vector


def calculate_buy_score(
    sneaker: Sneaker,
    market: MarketSnapshot | None,
    stocks: Sequence[StockSnapshot],
) -> tuple[int, BuyScoreParts, str | None]:
    premium_ratio = sneaker.market_price / max(sneaker.retail_price, 1.0)
    market_momentum = int(max(10.0, min(36.0, premium_ratio * 18.0)))

    liquidity = {
        "高": 24,
        "中": 16,
        "低": 9,
    }.get(sneaker.liquidity, 12)

    stock_correlation = _stock_component(sneaker.brand, stocks)
    culture_signal = int(sum(value for _, value in build_culture_vector(sneaker)[:5]) * 3.0)

    risk_penalty = 6
    if market is not None and market.bid_price > 0:
        spread_pct = (market.ask_price - market.bid_price) / market.bid_price * 100.0
        risk_penalty = int(max(2.0, min(18.0, spread_pct / 1.8)))

    raw_score = market_momentum + liquidity + stock_correlation + culture_signal - risk_penalty
    fallback_reason: str | None = None
    if not ai_available():
        raw_score -= 4
        fallback_reason = "AI unavailable: fallback calculator mode"

    final_score = int(max(35.0, min(99.0, raw_score)))
    parts: BuyScoreParts = {
        "market_momentum": market_momentum,
        "liquidity": liquidity,
        "stock_correlation": stock_correlation,
        "culture_signal": culture_signal,
        "risk_penalty": risk_penalty,
    }
    return final_score, parts, fallback_reason


def build_stock_correlation(stocks: Sequence[StockSnapshot]) -> tuple[list[CorrelationPoint], str]:
    rows: list[CorrelationPoint] = []
    if not stocks:
        return rows, "相関データが不足しています。"

    for row in stocks:
        same_direction = (row.change_pct >= 0 and row.index_change_pct >= 0) or (
            row.change_pct < 0 and row.index_change_pct < 0
        )
        gap = abs(row.change_pct - row.index_change_pct)
        magnitude = max(0.05, 1.0 - min(gap / 10.0, 0.95))
        correlation = magnitude if same_direction else -magnitude
        rows.append(
            {
                "ticker": row.ticker,
                "company": row.company,
                "correlation": round(correlation, 3),
                "relation": "positive" if correlation >= 0 else "negative",
                "change_pct": row.change_pct,
                "index_change_pct": row.index_change_pct,
            }
        )

    strongest = max(rows, key=lambda item: abs(item["correlation"]))
    summary = (
        f"{strongest['ticker']} が最も強い{strongest['relation']}相関 "
        f"({strongest['correlation']:+.2f})"
    )
    return rows, summary


def parse_intake_payload(intake_type: str, payload: str) -> tuple[int, list[IntakePreview], list[str]]:
    clean_payload = payload.strip()
    warnings: list[str] = []

    if intake_type == "csv":
        return _parse_csv(clean_payload)
    if intake_type == "url":
        preview = _parse_url(clean_payload, warnings)
        return 1, [preview], warnings
    if intake_type == "image":
        preview = _parse_image(clean_payload, warnings)
        return 1, [preview], warnings

    warnings.append("Unsupported intake type")
    return 0, [], warnings


def _stock_component(brand: str, stocks: Sequence[StockSnapshot]) -> int:
    if not stocks:
        return 8

    preferred_ticker = {
        "NIKE": "NKE",
        "ADIDAS": "ADDYY",
        "NEW BALANCE": "NKE",
        "ASICS": "ASCCY",
    }.get(brand.upper())

    target = next((row for row in stocks if row.ticker == preferred_ticker), None)
    if target is None:
        avg = sum(row.change_pct for row in stocks) / len(stocks)
        return int(max(6.0, min(20.0, 12.0 + avg * 2.0)))

    return int(max(6.0, min(20.0, 12.0 + target.change_pct * 2.5)))


def _parse_csv(payload: str) -> tuple[int, list[IntakePreview], list[str]]:
    warnings: list[str] = []
    if not payload:
        return 0, [], ["CSV payload is empty"]

    stream = StringIO(payload)
    reader = csv.DictReader(stream)
    if reader.fieldnames is None:
        return 0, [], ["CSV header is required"]

    preview: list[IntakePreview] = []
    total_rows = 0
    for index, row in enumerate(reader, start=1):
        raw_sku = (row.get("sku") or row.get("SKU") or "").strip()
        raw_model = (row.get("model") or row.get("MODEL") or "").strip()
        if not raw_sku and not raw_model:
            continue

        total_rows += 1
        sku = raw_sku or f"CSV-{index:03d}"
        model = raw_model or "Unknown Model"
        if len(preview) < 5:
            preview.append({"sku": sku, "model": model, "hint": "csv-intake"})

    if total_rows == 0:
        warnings.append("CSV has no usable rows")
    return total_rows, preview, warnings


def _parse_url(payload: str, warnings: list[str]) -> IntakePreview:
    parsed = urlparse(payload)
    if parsed.scheme not in {"http", "https"}:
        warnings.append("URL scheme should be http/https")
    domain = parsed.netloc or "unknown-source"
    checksum = sum(ord(char) for char in payload) % 100000
    return {
        "sku": f"URL-{checksum:05d}",
        "model": "URL Intake Candidate",
        "hint": domain,
    }


def _parse_image(payload: str, warnings: list[str]) -> IntakePreview:
    if payload.startswith("http://") or payload.startswith("https://"):
        hint = "remote-image"
    else:
        hint = "inline-image"

    if len(payload) < 12:
        warnings.append("Image payload is short; fallback estimation applied")

    checksum = sum(ord(char) for char in payload[:128]) % 100000
    return {
        "sku": f"IMG-{checksum:05d}",
        "model": "Image Intake Candidate",
        "hint": hint,
    }