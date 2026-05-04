"""
Lambda 2: Classify
Determina la severidad del ticket combinando priority_score y palabras clave
en la descripción.

Lógica:
- Palabras de alta severidad: urgent, down, unresponsive, critical, emergency,
  not working, outage, broken, crash, failure
- Si priority_score >= 75 O hay palabras clave de alta severidad → urgent
- Si priority_score >= 40 O hay palabras de severidad media → normal
- De lo contrario → low
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Palabras clave que elevan la severidad
HIGH_SEVERITY_KEYWORDS = [
    "urgent", "down", "unresponsive", "critical", "emergency",
    "not working", "outage", "broken", "crash", "failure", "stopped",
]

MEDIUM_SEVERITY_KEYWORDS = [
    "slow", "delayed", "error", "issue", "problem", "fail", "incorrect",
    "wrong", "missing", "cannot", "can't",
]


def _contains_keywords(text: str, keywords: list[str]) -> bool:
    """Verifica si el texto contiene alguna de las palabras clave (case-insensitive)."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _determine_severity(priority_score: float, description: str) -> str:
    """
    Determina la severidad basándose en score y palabras clave.
    Retorna: 'urgent', 'normal', o 'low'
    """
    has_high_keywords = _contains_keywords(description, HIGH_SEVERITY_KEYWORDS)
    has_medium_keywords = _contains_keywords(description, MEDIUM_SEVERITY_KEYWORDS)

    if priority_score >= 75 or has_high_keywords:
        return "urgent"
    elif priority_score >= 40 or has_medium_keywords:
        return "normal"
    else:
        return "low"


def lambda_handler(event: dict, context) -> dict:
    """
    Recibe el evento validado, calcula la severidad y la agrega al evento.
    """
    logger.info(f"Classify Lambda received event: {json.dumps(event)}")

    ticket_id = event.get("ticket_id", "unknown")
    priority_score = event["priority_score"]
    description = event["description"]

    severity = _determine_severity(priority_score, description)

    logger.info(
        f"[{ticket_id}] Classified as '{severity}' "
        f"(score={priority_score}, description='{description[:50]}...')"
    )

    return {
        **event,
        "severity": severity,
        "classification_details": {
            "score_used": priority_score,
            "high_keywords_found": _contains_keywords(description, HIGH_SEVERITY_KEYWORDS),
            "medium_keywords_found": _contains_keywords(description, MEDIUM_SEVERITY_KEYWORDS),
        },
    }