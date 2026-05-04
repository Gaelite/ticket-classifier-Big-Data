"""
Lambda 1: Validate
Verifica que el ticket de soporte tenga los campos requeridos y valores válidos.
- priority_score: debe ser numérico entre 0 y 100
- description: no puede estar vacía
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ValidationError(Exception):
    pass


def lambda_handler(event: dict, context) -> dict:
    """
    Recibe el evento completo, valida sus campos y agrega
    'validated': True antes de retornarlo.
    """
    logger.info(f"Validate Lambda received event: {json.dumps(event)}")

    ticket_id = event.get("ticket_id", "unknown")

    # Validar que priority_score exista y sea numérico entre 0-100
    priority_score = event.get("priority_score")
    if priority_score is None:
        raise ValidationError(f"[{ticket_id}] Missing required field: priority_score")

    if not isinstance(priority_score, (int, float)):
        raise ValidationError(
            f"[{ticket_id}] priority_score must be numeric, got: {type(priority_score).__name__}"
        )

    if not (0 <= priority_score <= 100):
        raise ValidationError(
            f"[{ticket_id}] priority_score must be between 0 and 100, got: {priority_score}"
        )

    # Validar que description exista y no esté vacía
    description = event.get("description", "").strip()
    if not description:
        raise ValidationError(f"[{ticket_id}] description cannot be empty")

    # Validar que customer exista
    customer = event.get("customer", "").strip()
    if not customer:
        raise ValidationError(f"[{ticket_id}] customer field is required")

    logger.info(f"[{ticket_id}] Ticket passed validation successfully")

    # Agregar campo al evento y retornarlo completo
    return {
        **event,
        "validated": True,
        "validation_message": "All fields passed validation",
    }