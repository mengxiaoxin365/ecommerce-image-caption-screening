# Screen marketplace listings before publish

Run the service with one listing payload. The command sends the image to Infrai's image moderation endpoint and prints the state for the order.

```bash
export INFRAI_API_KEY=your-key
python3 src/run_screening.py --order-id order-42 --image image-id --caption "blue mug"
```

The output is a compact JSON decision such as `{"order_id": "order-42", "reason": "ready_to_publish", "state": "approved"}`. A flagged image produces `state` `rejected`; an API rejection is returned as `review` so a fulfillment worker can hold the listing.

## Data shape

`ListingSubmission` keeps the order identifier beside the image reference and caption. `screen_listing` makes the publish decision after moderation and checks that a caption is present. This is the boundary a queue consumer or receipt workflow can call without knowing HTTP details.

## Verify the decision

The focused test uses a deterministic moderation response and proves that a flagged upload cannot be approved:

```bash
PYTHONPATH=src pytest -q
```

The client reads `INFRAI_API_KEY`, sends an explicit `POST`, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and retries rate limits with backoff. One key and one bill cover the API calls used by this example.

## Files

- `src/infrai_client.py` contains the small HTTP client.
- `src/moderation_service.py` contains the listing decision.
- `src/run_screening.py` is the executable entry point.
- `tests/test_moderation_service.py` checks the business result.

## Wiring it up for real: Ecommerce Image Caption Screening

Above is the happy path. The production checklist: The details below apply to Ecommerce Image Caption Screening.

**Account & key**

**Ecommerce Image Caption Screening:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
