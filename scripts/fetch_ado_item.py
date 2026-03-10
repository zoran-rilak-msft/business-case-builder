"""Fetch an Azure DevOps work item and output structured JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

from scripts.models import AdoItemOutput, LinkedItem

# Relation types we care about
_CHILD_REL = "System.LinkTypes.Hierarchy-Forward"
_RELATED_REL = "System.LinkTypes.Related"

_RELATION_LABELS = {
    _CHILD_REL: "Child",
    _RELATED_REL: "Related",
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch an ADO work item as JSON.")
    parser.add_argument("--item-id", type=int, required=True, help="ADO work item ID")
    parser.add_argument(
        "--org",
        required=True,
        help="ADO organization URL (e.g. https://dev.azure.com/myorg)",
    )
    return parser.parse_args(argv)


def _extract_assigned_to(field_value: object) -> str | None:
    if field_value is None:
        return None
    if isinstance(field_value, dict):
        return field_value.get("displayName")
    return str(field_value)


def _extract_tags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.split(";") if t.strip()]


def _work_item_id_from_url(url: str) -> int | None:
    """Extract the trailing integer ID from an ADO relation URL."""
    try:
        return int(url.rstrip("/").rsplit("/", 1)[-1])
    except (ValueError, IndexError):
        return None


def fetch_work_item(item_id: int, org_url: str) -> AdoItemOutput:
    """Connect to ADO, fetch a work item, and return an AdoItemOutput."""
    pat = os.environ.get("ADO_PAT")
    if not pat:
        print(
            "Error: ADO_PAT environment variable is not set. "
            "Set it to your Azure DevOps Personal Access Token.",
            file=sys.stderr,
        )
        sys.exit(1)

    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    wit_client = connection.clients.get_work_item_tracking_client()

    try:
        work_item = wit_client.get_work_item(item_id, expand="all")
    except Exception as exc:
        print(f"Error: Could not fetch work item {item_id}: {exc}", file=sys.stderr)
        sys.exit(1)

    fields = work_item.fields

    # Resolve linked items (children + related)
    linked_items: list[LinkedItem] = []
    if work_item.relations:
        ids_to_fetch: list[tuple[int, str]] = []
        for rel in work_item.relations:
            rel_type = getattr(rel, "rel", None)
            if rel_type in _RELATION_LABELS:
                target_url = getattr(rel, "url", "")
                target_id = _work_item_id_from_url(target_url)
                if target_id is not None:
                    ids_to_fetch.append((target_id, _RELATION_LABELS[rel_type]))

        for target_id, relation_label in ids_to_fetch:
            try:
                linked_wi = wit_client.get_work_item(target_id)
                linked_items.append(
                    LinkedItem(
                        id=target_id,
                        title=linked_wi.fields["System.Title"],
                        relation_type=relation_label,
                    )
                )
            except Exception:
                linked_items.append(
                    LinkedItem(
                        id=target_id,
                        title="<unavailable>",
                        relation_type=relation_label,
                    )
                )

    return AdoItemOutput(
        id=work_item.id,
        title=fields["System.Title"],
        description=fields.get("System.Description", "") or "",
        acceptance_criteria=fields.get("Microsoft.VSTS.Common.AcceptanceCriteria"),
        work_item_type=fields["System.WorkItemType"],
        state=fields["System.State"],
        assigned_to=_extract_assigned_to(fields.get("System.AssignedTo")),
        tags=_extract_tags(fields.get("System.Tags")),
        linked_items=linked_items,
    )


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    result = fetch_work_item(args.item_id, args.org)
    print(json.dumps(result.model_dump(), indent=2))
    print(
        f"Fetched work item {result.id}: {result.title} ({result.work_item_type})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
