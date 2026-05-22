"""clean — (stretch) bulk terminate resources matching a tag.

WARNING — DESIGN-FOR-SAFETY
---------------------------
This is the most dangerous command in the CLI. Get the contract right:

  1. DEFAULT IS DRY-RUN. Without --apply the command MUST NOT touch resources.
     It only lists what WOULD be deleted.
  2. Even with --apply, you should consider printing a summary count first
     ("about to terminate N EC2 + M volumes — proceed?"), though for this
     starter a hard `--apply` flag is enough.
  3. Never use this with a tag you don't fully own. Reflection prompt in
     README covers the blast-radius scenario.

WHAT YOU MUST BUILD
-------------------
1. `_find_targets(tag_key, tag_val)` — return a dict like:
     {"ec2": [<instance ids in non-terminal state>],
      "volume": [<volume ids in 'available' state only>]}
   Skip terminated/shutting-down instances (already gone).
   Skip in-use volumes (can't delete while attached — would error anyway).

2. `run(args)` — call _find_targets, print the plan, then either:
     - bail with "(dry-run — pass --apply to ...)"  (default)
     - or actually terminate (when --apply)

HELPERS YOU CAN USE
-------------------
From commands._common:
  parse_kv(s) -> (k, v)

AWS APIS YOU'LL NEED
--------------------
- ec2.describe_instances() + describe_volumes() — same as list_cmd
- ec2.terminate_instances(InstanceIds=[...])
- ec2.delete_volume(VolumeId=...)  (per volume, no bulk API)

VERIFY
------
    pytest tests/test_clean.py -v
"""
import boto3

from commands._common import parse_kv, tags_to_dict


def _find_targets(tag_key, tag_val):

    ec2 = boto3.client("ec2")

    targets = {
        "ec2": [],
        "volume": [],
    }

    resp = ec2.describe_instances()

    for reservation in resp["Reservations"]:

        for instance in reservation["Instances"]:

            state = instance["State"]["Name"]

            if state in [
                "terminated",
                "shutting-down",
            ]:
                continue

            tags = tags_to_dict(
                instance.get("Tags", [])
            )

            if tags.get(tag_key) == tag_val:

                targets["ec2"].append(
                    instance["InstanceId"]
                )

    resp = ec2.describe_volumes()

    for volume in resp["Volumes"]:

        if volume["State"] != "available":
            continue

        tags = tags_to_dict(
            volume.get("Tags", [])
        )

        if tags.get(tag_key) == tag_val:

            targets["volume"].append(
                volume["VolumeId"]
            )

    return targets


def run(args):

    tag_key, tag_val = parse_kv(
        args.tag
    )

    targets = _find_targets(
        tag_key,
        tag_val,
    )

    print("Plan:")

    print(
        f"EC2: {len(targets['ec2'])}"
    )

    print(
        f"Volumes: {len(targets['volume'])}"
    )

    total = (
        len(targets["ec2"]) +
        len(targets["volume"])
    )

    if total == 0:

        print("Nothing to clean")

        return

    if not args.apply:

        print(
            "(dry-run — pass --apply to execute)"
        )

        return

    ec2 = boto3.client("ec2")

    if targets["ec2"]:

        ec2.terminate_instances(
            InstanceIds=targets["ec2"]
        )

        print(
            f"Terminated "
            f"{len(targets['ec2'])} EC2 instance(s)"
        )

    for vid in targets["volume"]:

        ec2.delete_volume(
            VolumeId=vid
        )

    if targets["volume"]:

        print(
            f"Deleted "
            f"{len(targets['volume'])} volume(s)"
        )