from moderation_service import ListingSubmission, ModerationDecision, screen_listing


class StubClient:
    def moderate_image(self, image):
        return {"flagged": True}


def test_flagged_upload_is_rejected_before_publish():
    submission = ListingSubmission("order-42", "img_42", "blue mug")
    assert screen_listing(submission, StubClient()) == ModerationDecision("order-42", "rejected", "image_flagged")
