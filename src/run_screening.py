import argparse
import json

from infrai_client import InfraiClient
from moderation_service import ListingSubmission, screen_listing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order-id", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--caption", required=True)
    args = parser.parse_args()
    decision = screen_listing(ListingSubmission(args.order_id, args.image, args.caption), InfraiClient())
    print(json.dumps(decision.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
