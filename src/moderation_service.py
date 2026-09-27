from dataclasses import dataclass
from typing import Any, Dict

from infrai_client import InfraiClient, InfraiError


@dataclass
class ListingSubmission:
    order_id: str
    image: str
    caption: str


@dataclass
class ModerationDecision:
    order_id: str
    state: str
    reason: str


def screen_listing(submission: ListingSubmission, client: InfraiClient) -> ModerationDecision:
    try:
        result: Dict[str, Any] = client.moderate_image(submission.image)
    except InfraiError as exc:
        return ModerationDecision(submission.order_id, "review", exc.code)
    flagged = bool(result.get("flagged", result.get("blocked", False)))
    if flagged:
        return ModerationDecision(submission.order_id, "rejected", "image_flagged")
    if not submission.caption.strip():
        return ModerationDecision(submission.order_id, "rejected", "caption_required")
    return ModerationDecision(submission.order_id, "approved", "ready_to_publish")
