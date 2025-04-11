import os
import glob
import json
import statistics
from datetime import datetime
from collections import defaultdict

LOG_DIR = "./log"
pattern = os.path.join(LOG_DIR, "keyboard_log_*.json")
home_row_keys = {"a", "s", "d", "f", "j", "k", "l", ";"}

key_down_times = {}
all_hold_durations = defaultdict(list)
home_row_hold_durations = defaultdict(list)
home_row_tap_durations = defaultdict(list)


def parse_timestamp(ts):
    if isinstance(ts, float):
        return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        try:
            return datetime.strptime(ts, "%Y%m%d_%H%M%S")
        except ValueError:
            try:
                return datetime.fromisoformat(ts)
            except ValueError:
                return None
    return None


# Read and parse each log file
for filepath in glob.glob(pattern):
    try:
        with open(filepath, "r") as f:
            raw = f.read().strip()
            outer = json.loads(raw)
            if isinstance(outer, str):
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

print("\n=== Key Timing Analysis ===")
print("This section shows how long you hold each key when typing.")
print("Average hold time (avg): The typical duration you press each key")
print("Standard deviation (std): How consistent your timing is (lower is better)")
print("Minimum (min) and Maximum (max): Your fastest and slowest key presses")
print("\nKey statistics (sorted by frequency):")
print("-" * 80)

for key, durations in sorted(all_hold_durations.items(), key=lambda x: -len(x[1])):
    if len(durations) < 2:
        print(
            f"Key '{key}': {len(durations)} presses, avg hold = {durations[0]:.4f} sec"
        )
    else:
        avg = statistics.mean(durations)
        std = statistics.stdev(durations)
        print(
            f"Key '{key}': {len(durations)} presses, "
            f"avg = {avg:.4f}s, std = {std:.4f}s, "
            f"min = {min(durations):.4f}s, max = {max(durations):.4f}s"
        )

# Home row modifier analysis
print("\n=== Home Row Modifier Analysis ===")
print(
    "This section focuses on your home row keys (a,s,d,f,j,k,l,;) which are often used as modifiers."
)
print("Taps: Quick presses (under 200ms) - these should be regular keystrokes")
print("Holds: Longer presses (over 200ms) - these are likely modifier activations")
print("\nHome row key statistics:")
print("-" * 80)

# Analyze taps and holds to extract thresholds
tap_ceiling = 0
hold_floor = float("inf")

for key in sorted(home_row_keys):
    taps = home_row_tap_durations.get(key, [])
    holds = home_row_hold_durations.get(key, [])

    def stats(label, data):
        if not data:
            return f"0 {label}s"
        avg = statistics.mean(data)
        std = statistics.stdev(data) if len(data) > 1 else 0
        min_v = min(data)
        max_v = max(data)
        return (
            f"{len(data)} {label}s "
            f"(avg = {avg:.4f}s, std = {std:.4f}s, "
            f"min = {min_v:.4f}s, max = {max_v:.4f}s)"
        )

    if taps:
        tap_max = max(taps)
        tap_std = statistics.stdev(taps) if len(taps) > 1 else 0
        tap_ceiling = max(tap_ceiling, tap_max + tap_std)

    if holds:
        hold_min = min(holds)
        hold_floor = min(hold_floor, hold_min)

    tap_stats = stats("tap", taps)
    hold_stats = stats("hold", holds)

    print(f"Key '{key}': {tap_stats}, {hold_stats}")

# Suggested configuration
print("\n=== Suggested ZMK Configuration ===")
print(
    "Based on your typing patterns, here are suggested timing values for your ZMK config."
)
print(
    "These values are in milliseconds and are calculated from your actual typing data."
)
print("\nDifficulty Levels:")
print("1: Novice (500ms) - Best for beginners")
print("2: Slower (400ms) - Good for learning")
print("3: Normal (300ms) - Standard typing speed")
print("4: Faster (200ms) - For experienced typists")
print("5: Expert (100ms) - For very fast typists")
print("0: Custom (150ms) - Sunaku's personal settings")
print("\nSuggested values:")
print("-" * 80)

# Conservative recommendation based on tap + std and hold min
safe_gap_ms = 10
raw_tap_resolution = int((tap_ceiling * 1000) + safe_gap_ms)
tapping_resolution = max(100, min(500, raw_tap_resolution))

# Difficulty level logic
if tapping_resolution >= 500:
    difficulty_level = 1
elif tapping_resolution >= 400:
    difficulty_level = 2
elif tapping_resolution >= 300:
    difficulty_level = 3
elif tapping_resolution >= 200:
    difficulty_level = 4
elif tapping_resolution >= 100:
    difficulty_level = 5
else:
    difficulty_level = 0

print(f"#define DIFFICULTY_LEVEL {difficulty_level}  // Based on your typing speed")
print(f"#define TAPPING_RESOLUTION {tapping_resolution}")

# Other defines derived from tapping resolution
index_holding_time = tapping_resolution + 20
middy_holding_time = index_holding_time + 40
ringy_holding_time = middy_holding_time + 30
pinky_holding_time = ringy_holding_time + 20

print(f"#define INDEX_HOLDING_TIME {index_holding_time}")
print(f"#define MIDDY_HOLDING_TIME {middy_holding_time}")
print(f"#define RINGY_HOLDING_TIME {ringy_holding_time}")
print(f"#define PINKY_HOLDING_TIME {pinky_holding_time}")

print("\nAdditional recommended settings:")
print(
    f"#define HOMEY_STREAK_DECAY {tapping_resolution}  // Prevents unintended mods during typing"
)
print(f"#define HOMEY_REPEAT_DECAY {tapping_resolution + 150}  // For key auto-repeat")
print(
    f"#define INDEX_STREAK_DECAY {max(0, tapping_resolution - 50)}  // Faster shift activation"
)
print(
    f"#define INDEX_REPEAT_DECAY {tapping_resolution + 150}  // For shift auto-repeat"
)
print(f"#define PLAIN_HOLDING_TIME {tapping_resolution + 50}")
print(f"#define PLAIN_REPEAT_DECAY {tapping_resolution + 150}")
print(f"#define SPACE_HOLDING_TIME {tapping_resolution + 20}")
print(f"#define SPACE_REPEAT_DECAY {tapping_resolution}")

print("\nNote: These are starting values. You may need to adjust them based on:")
print("- Your typing speed and style")
print("- The specific keyboard and switches you're using")
print("- Your personal preference for tap vs hold behavior")
print("\nFor more information about these settings, see the ZMK documentation.")
