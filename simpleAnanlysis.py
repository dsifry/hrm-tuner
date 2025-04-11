import os
import glob
import json
import statistics
from datetime import datetime
from collections import defaultdict

LOG_DIR = './log'
pattern = os.path.join(LOG_DIR, 'keyboard_log_*.json')
home_row_keys = {'a', 's', 'd', 'f', 'j', 'k', 'l', ';'}

key_down_times = {}
all_hold_durations = defaultdict(list)
home_row_hold_durations = defaultdict(list)
home_row_tap_durations = defaultdict(list)

def parse_timestamp(ts):
    if isinstance(ts, float):  # high-precision format
        return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        try:
            return datetime.strptime(ts, "%Y%m%d_%H%M%S")  # legacy format
        except ValueError:
            try:
                return datetime.fromisoformat(ts)
            except ValueError:
                return None
    return None

# Read and parse each log file
for filepath in glob.glob(pattern):
    try:
        with open(filepath, 'r') as f:
            raw = f.read().strip()
            outer = json.loads(raw)
            if isinstance(outer, str):  # Handle double-encoded legacy format
                outer = json.loads(outer)
            events = outer.get("records", [])
    except Exception:
        continue

    for event in events:
        key = event.get("button")
        ts_raw = event.get("timestamp")
        is_press = event.get("is_on_press")

        if not key or ts_raw is None:
            continue

        timestamp = parse_timestamp(ts_raw)
        if not timestamp:
            continue

        if is_press:
            key_down_times[key] = timestamp
        elif key in key_down_times:
            duration = (timestamp - key_down_times.pop(key)).total_seconds()
            all_hold_durations[key].append(duration)

            if key in home_row_keys:
                if duration < 0.200:
                    home_row_tap_durations[key].append(duration)
                else:
                    home_row_hold_durations[key].append(duration)

# ---- Output ---- #

# Summary 1: General key stats
print("\n=== Full Key Hold Timing Analysis ===")
for key, durations in sorted(all_hold_durations.items(), key=lambda x: -len(x[1])):
    if len(durations) < 2:
        print(f"Key '{key}': {len(durations)} presses, avg hold = {durations[0]:.4f} sec")
    else:
        avg = statistics.mean(durations)
        std = statistics.stdev(durations)
        print(
            f"Key '{key}': {len(durations)} presses, "
            f"avg = {avg:.4f}s, std = {std:.4f}s, "
            f"min = {min(durations):.4f}s, max = {max(durations):.4f}s"
        )

# Summary 2: Home row keys - tap vs hold breakdown
print("\n=== Home Row Modifier Tap vs Hold Classification ===")
for key in sorted(home_row_keys):
    taps = home_row_tap_durations.get(key, [])
    holds = home_row_hold_durations.get(key, [])

    def stats(label, data):
        if not data:
            return f"0 {label}s"
        avg = statistics.mean(data)
        std = statistics.stdev(data) if len(data) > 1 else 0
        return (
            f"{len(data)} {label}s "
            f"(avg = {avg:.4f}s, std = {std:.4f}s, "
            f"min = {min(data):.4f}s, max = {max(data):.4f}s)"
        )

    tap_stats = stats("tap", taps)
    hold_stats = stats("hold", holds)

    print(f"Key '{key}': {tap_stats}, {hold_stats}")

