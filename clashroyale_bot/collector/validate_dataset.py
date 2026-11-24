"""Dataset validation for RL training data."""

import argparse
import gzip
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def validate_dataset(data_file: Path) -> dict[str, Any]:
    """
    Validate a dataset file and return a report.

    Args:
        data_file: Path to the JSONL.gz dataset file.

    Returns:
        Dictionary containing validation report with statistics and warnings.
    """
    frames = []
    frame_ids = []

    # Read all frames
    with gzip.open(data_file, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            frame = json.loads(line)
            frames.append(frame)
            frame_ids.append(frame.get("frame_id", 0))

    total_frames = len(frames)

    if total_frames == 0:
        return {
            "frame_count": 0,
            "warnings": ["Dataset is empty"],
            "class_balance": {"no_action": 0.0},
            "reward_stats": {},
            "screen_distribution": {},
            "action_distribution": {},
            "missing_frames": [],
            "duplicate_frames": [],
        }

    # Class balance: no-action vs action frames
    action_count = sum(1 for f in frames if f.get("action") is not None)
    no_action_count = total_frames - action_count
    no_action_ratio = no_action_count / total_frames

    class_balance = {
        "no_action": no_action_ratio,
        "action": action_count / total_frames,
        "no_action_count": no_action_count,
        "action_count": action_count,
    }

    warnings = []
    if no_action_ratio > 0.8:
        warnings.append(f"High no-action ratio: {no_action_ratio:.1%} (consider more action frames)")

    # Screen distribution
    screen_distribution = Counter(f.get("screen", "UNKNOWN") for f in frames)

    # Action distribution
    action_distribution = Counter()
    for f in frames:
        action = f.get("action")
        if action:
            action_distribution[action.get("card", "unknown")] += 1
        else:
            action_distribution["no_action"] += 1

    # Reward statistics
    reward_keys = [
        "elixir_delta",
        "tower_dmg_dealt",
        "tower_dmg_taken",
        "unit_value_killed",
        "unit_value_lost",
        "win_bonus",
        "loss_penalty",
    ]
    reward_stats = {}
    for key in reward_keys:
        values = [f.get("reward", {}).get(key, 0.0) for f in frames]
        if values:
            reward_stats[key] = {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "sum": sum(values),
            }

    # Missing/duplicate frame detection
    if frame_ids:
        min_id = min(frame_ids)
        max_id = max(frame_ids)
        expected_ids = set(range(min_id, max_id + 1))
        actual_ids = set(frame_ids)

        missing_frames = sorted(expected_ids - actual_ids)

        # Find duplicates
        id_counts = Counter(frame_ids)
        duplicate_frames = sorted([fid for fid, count in id_counts.items() if count > 1])
    else:
        missing_frames = []
        duplicate_frames = []

    if missing_frames:
        warnings.append(f"Missing frame_ids: {missing_frames[:10]}{'...' if len(missing_frames) > 10 else ''}")
    if duplicate_frames:
        warnings.append(f"Duplicate frame_ids: {duplicate_frames[:10]}{'...' if len(duplicate_frames) > 10 else ''}")

    return {
        "frame_count": total_frames,
        "class_balance": class_balance,
        "warnings": warnings,
        "reward_stats": reward_stats,
        "screen_distribution": dict(screen_distribution),
        "action_distribution": dict(action_distribution),
        "missing_frames": missing_frames,
        "duplicate_frames": duplicate_frames,
    }


def main() -> int:
    """Main entry point for validate_dataset CLI."""
    parser = argparse.ArgumentParser(description="Validate Clash Royale bot dataset")
    parser.add_argument("data_file", type=Path, help="Path to JSONL.gz dataset file")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    args = parser.parse_args()

    if not args.data_file.exists():
        print(f"Error: File not found: {args.data_file}", file=sys.stderr)
        return 1

    try:
        report = validate_dataset(args.data_file)
    except Exception as e:
        print(f"Error validating dataset: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Print human-readable summary
        print(f"\n=== Dataset Validation Report ===")
        print(f"File: {args.data_file}")
        print(f"Total frames: {report['frame_count']}")
        print(f"\nClass Balance:")
        print(f"  No-action: {report['class_balance']['no_action']:.1%} ({report['class_balance']['no_action_count']})")
        print(f"  Action:    {report['class_balance']['action']:.1%} ({report['class_balance']['action_count']})")

        print(f"\nScreen Distribution:")
        for screen, count in report['screen_distribution'].items():
            print(f"  {screen}: {count}")

        print(f"\nAction Distribution:")
        for action, count in report['action_distribution'].items():
            print(f"  {action}: {count}")

        print(f"\nReward Statistics:")
        for key, stats in report['reward_stats'].items():
            print(f"  {key}: min={stats['min']:.3f}, max={stats['max']:.3f}, mean={stats['mean']:.3f}, sum={stats['sum']:.3f}")

        if report['missing_frames']:
            print(f"\nMissing frame_ids: {report['missing_frames'][:20]}{'...' if len(report['missing_frames']) > 20 else ''}")
        if report['duplicate_frames']:
            print(f"Duplicate frame_ids: {report['duplicate_frames'][:20]}{'...' if len(report['duplicate_frames']) > 20 else ''}")

        if report['warnings']:
            print(f"\nWarnings:")
            for warning in report['warnings']:
                print(f"  ⚠ {warning}")
        else:
            print(f"\nNo warnings.")

    return 0


if __name__ == "__main__":
    sys.exit(main())