#!/usr/bin/env python3
"""
HRM-specific analysis for 'f', 'j', and 'SPACE' keys.
Analyzes tap vs hold patterns, HRM activation timing, and generates
ZMK configuration recommendations.

NOTE: This analysis is purely timing-based. We don't care about typos,
spelling errors, or what you actually typed - only the timing patterns!
Type fast and naturally - errors are expected and ignored!
"""

import os
import glob
import json
import statistics
import argparse
from datetime import datetime
from collections import defaultdict

LOG_DIR = "./log"
pattern = os.path.join(LOG_DIR, "keyboard_log_*.json")

# Keys we're specifically analyzing as HRM modifiers
HRM_KEYS = {"f", "j", "SPACE"}

# Left hand keys (for j+left combinations)
LEFT_HAND_KEYS = {"1", "2", "3", "4", "5", "q", "w", "e", "r", "t",
                  "a", "s", "d", "f", "g", "z", "x", "c", "v", "b",
                  "`", "[", "]"}

# Right hand keys (for f+right combinations)
RIGHT_HAND_KEYS = {"6", "7", "8", "9", "0", "p", "y", "u", "i", "o",
                   "h", "j", "k", "l", ";", "n", "m", ",", ".", "/", "\\"}

# Keys for space combinations (m for ', n for ")
SPACE_COMBO_KEYS = {"m", "n"}


def parse_timestamp(ts):
    """Parse various timestamp formats to datetime."""
    if isinstance(ts, float):
        return ts  # Return raw timestamp for precision
    elif isinstance(ts, str):
        try:
            dt = datetime.strptime(ts, "%Y%m%d_%H%M%S")
            return dt.timestamp()
        except ValueError:
            try:
                dt = datetime.fromisoformat(ts)
                return dt.timestamp()
            except ValueError:
                return None
    return None


class HRMAnalyzer:
    def __init__(self):
        self.key_events = []  # All events in order
        self.key_down_times = {}  # Currently pressed keys

        # Pure hold durations (key down to key up, no other keys pressed)
        self.pure_taps = defaultdict(list)

        # HRM hold patterns (key held while another key is pressed)
        self.hrm_holds = defaultdict(list)

        # Time from HRM key down to next key press
        self.hrm_activation_times = defaultdict(list)

        # All hold durations for each key
        self.all_hold_durations = defaultdict(list)

        # Track overlapping key sequences
        self.overlap_sequences = []

    def load_logs(self):
        """Load all keyboard log files."""
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, "r") as f:
                    raw = f.read().strip()
                    outer = json.loads(raw)
                    if isinstance(outer, str):
                        outer = json.loads(outer)
                    events = outer.get("records", [])

                    for event in events:
                        key = event.get("button")
                        ts_raw = event.get("timestamp")
                        is_press = event.get("is_on_press")

                        if not key or ts_raw is None:
                            continue

                        timestamp = parse_timestamp(ts_raw)
                        if timestamp is None:
                            continue

                        self.key_events.append({
                            "key": key,
                            "timestamp": timestamp,
                            "is_press": is_press
                        })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue

        # Sort events by timestamp
        self.key_events.sort(key=lambda x: x["timestamp"])

    def analyze_events(self):
        """Analyze key events to detect HRM patterns."""
        currently_held = {}  # key -> down_timestamp

        for i, event in enumerate(self.key_events):
            key = event["key"]
            timestamp = event["timestamp"]
            is_press = event["is_press"]

            if is_press:
                # Key pressed down
                currently_held[key] = timestamp

                # Check if this is pressed while an HRM key is held
                for hrm_key in HRM_KEYS:
                    if hrm_key in currently_held and hrm_key != key:
                        # Calculate time from HRM key down to this key press
                        activation_time = timestamp - currently_held[hrm_key]
                        self.hrm_activation_times[hrm_key].append(activation_time)

            else:
                # Key released
                if key not in currently_held:
                    continue

                down_time = currently_held[key]
                hold_duration = timestamp - down_time
                self.all_hold_durations[key].append(hold_duration)

                # Check if this was a pure tap or an HRM hold
                # Pure tap = no other keys pressed during hold
                # HRM hold = other keys pressed while this was held

                other_keys_during_hold = []
                for other_key, other_down_time in currently_held.items():
                    if other_key != key and other_down_time > down_time:
                        other_keys_during_hold.append(other_key)

                if key in HRM_KEYS:
                    if other_keys_during_hold:
                        # This was an HRM hold (modifier use)
                        self.hrm_holds[key].append(hold_duration)
                    else:
                        # This was a pure tap (normal key use)
                        self.pure_taps[key].append(hold_duration)

                del currently_held[key]

    def print_statistics(self):
        """Print detailed statistics for HRM keys."""
        print("\n" + "="*80)
        print("HRM KEY ANALYSIS: 'f', 'j', and 'SPACE'")
        print("="*80)

        for key in sorted(HRM_KEYS):
            print(f"\n{'─'*80}")
            print(f"Key: '{key}'")
            print(f"{'─'*80}")

            # Pure taps (normal typing)
            taps = self.pure_taps.get(key, [])
            if taps:
                taps_ms = [t * 1000 for t in taps]
                print(f"\nPURE TAPS (normal typing, no other keys held):")
                print(f"  Count: {len(taps)}")
                print(f"  Average: {statistics.mean(taps_ms):.1f}ms")
                print(f"  Std Dev: {statistics.stdev(taps_ms) if len(taps) > 1 else 0:.1f}ms")
                print(f"  Min: {min(taps_ms):.1f}ms")
                print(f"  Max: {max(taps_ms):.1f}ms")
                print(f"  95th percentile: {sorted(taps_ms)[int(len(taps_ms) * 0.95)] if len(taps_ms) > 1 else max(taps_ms):.1f}ms")
            else:
                print(f"\nPURE TAPS: No data")

            # HRM holds (modifier use)
            holds = self.hrm_holds.get(key, [])
            if holds:
                holds_ms = [h * 1000 for h in holds]
                print(f"\nHRM HOLDS (used as modifier with other keys):")
                print(f"  Count: {len(holds)}")
                print(f"  Average: {statistics.mean(holds_ms):.1f}ms")
                print(f"  Std Dev: {statistics.stdev(holds_ms) if len(holds) > 1 else 0:.1f}ms")
                print(f"  Min: {min(holds_ms):.1f}ms")
                print(f"  Max: {max(holds_ms):.1f}ms")
                print(f"  5th percentile: {sorted(holds_ms)[int(len(holds_ms) * 0.05)] if len(holds_ms) > 1 else min(holds_ms):.1f}ms")
            else:
                print(f"\nHRM HOLDS: No data")

            # Activation times (time from key down to next key press)
            activations = self.hrm_activation_times.get(key, [])
            if activations:
                act_ms = [a * 1000 for a in activations]
                print(f"\nACTIVATION TIMING (key down → next key press):")
                print(f"  Count: {len(activations)}")
                print(f"  Average: {statistics.mean(act_ms):.1f}ms")
                print(f"  Std Dev: {statistics.stdev(act_ms) if len(act_ms) > 1 else 0:.1f}ms")
                print(f"  Min: {min(act_ms):.1f}ms")
                print(f"  Max: {max(act_ms):.1f}ms")
                print(f"  95th percentile: {sorted(act_ms)[int(len(act_ms) * 0.95)] if len(act_ms) > 1 else max(act_ms):.1f}ms")
            else:
                print(f"\nACTIVATION TIMING: No data")

    def calculate_recommendations(self):
        """Calculate ZMK timing recommendations."""
        print("\n" + "="*80)
        print("ZMK CONFIGURATION RECOMMENDATIONS")
        print("="*80)

        recommendations = {}

        for key in sorted(HRM_KEYS):
            taps = self.pure_taps.get(key, [])
            holds = self.hrm_holds.get(key, [])
            activations = self.hrm_activation_times.get(key, [])

            if not taps and not holds:
                print(f"\nKey '{key}': No data available")
                continue

            print(f"\n{'─'*80}")
            print(f"Recommendations for '{key}':")
            print(f"{'─'*80}")

            # Calculate tapping-term-ms
            # This should be above max tap time but below min hold time
            tapping_term = None
            if taps:
                taps_ms = [t * 1000 for t in taps]
                max_tap = max(taps_ms)
                # Add 2 std deviations for safety
                std_tap = statistics.stdev(taps_ms) if len(taps) > 1 else 0
                tap_threshold = max_tap + (2 * std_tap)

                # If we have holds, make sure we're below the minimum hold
                if holds:
                    holds_ms = [h * 1000 for h in holds]
                    min_hold = min(holds_ms)

                    # Find the sweet spot between max tap and min hold
                    if tap_threshold < min_hold:
                        tapping_term = int((tap_threshold + min_hold) / 2)
                    else:
                        # Overlapping distributions - use conservative value
                        tapping_term = int(tap_threshold)
                        print(f"  ⚠ WARNING: Tap and hold times overlap!")
                        print(f"    Max tap: {max_tap:.1f}ms, Min hold: {min_hold:.1f}ms")
                else:
                    tapping_term = int(tap_threshold)
            elif holds:
                # No tap data, use conservative value below min hold
                holds_ms = [h * 1000 for h in holds]
                min_hold = min(holds_ms)
                tapping_term = int(min_hold * 0.8)  # 80% of min hold

            if tapping_term:
                # Clamp to reasonable range
                tapping_term = max(100, min(300, tapping_term))
                recommendations[key] = {"tapping_term": tapping_term}
                print(f"\n  tapping-term-ms = {tapping_term}")

            # Calculate quick-tap-ms
            # This should be below typical tap time to allow rapid tapping
            if taps:
                taps_ms = [t * 1000 for t in taps]
                avg_tap = statistics.mean(taps_ms)
                quick_tap = int(avg_tap * 1.2)  # 120% of average tap
                quick_tap = max(100, min(200, quick_tap))
                recommendations[key]["quick_tap"] = quick_tap
                print(f"  quick-tap-ms = {quick_tap}")

            # Calculate require-prior-idle-ms
            # This helps prevent accidental activation during rolling/sliding
            if activations:
                act_ms = [a * 1000 for a in activations]
                # Use 5th percentile - faster than this is likely a roll
                percentile_5 = sorted(act_ms)[int(len(act_ms) * 0.05)] if len(act_ms) > 1 else min(act_ms)
                prior_idle = int(percentile_5 * 0.8)
                prior_idle = max(50, min(150, prior_idle))
                recommendations[key]["prior_idle"] = prior_idle
                print(f"  require-prior-idle-ms = {prior_idle}")
                print(f"    (prevents activation if key pressed within {prior_idle}ms of another)")

            # Recommend flavor
            if taps and holds:
                taps_ms = [t * 1000 for t in taps]
                holds_ms = [h * 1000 for h in holds]
                avg_tap = statistics.mean(taps_ms)
                avg_hold = statistics.mean(holds_ms)

                # If hold times are much longer than taps, use tap-preferred
                if avg_hold > avg_tap * 2:
                    flavor = "tap-preferred"
                else:
                    flavor = "balanced"

                recommendations[key]["flavor"] = flavor
                print(f"  flavor = \"{flavor}\"")

        return recommendations

    def generate_zmk_config(self, recommendations):
        """Generate ZMK configuration code."""
        print("\n" + "="*80)
        print("COPY-PASTE ZMK CONFIG")
        print("="*80)
        print("\n// Add this to your ZMK keymap file:")
        print("\nbehaviors {")

        for key, rec in recommendations.items():
            key_name = key.upper() if key != "SPACE" else "SPACE"
            print(f"\n  // Home row modifier for '{key}'")
            print(f"  hrm_{key}: hrm_{key} {{")
            print(f"    compatible = \"zmk,behavior-hold-tap\";")
            print(f"    label = \"HRM_{key_name}\";")
            print(f"    #binding-cells = <2>;")
            print(f"    tapping-term-ms = <{rec.get('tapping_term', 200)}>;")
            if "quick_tap" in rec:
                print(f"    quick-tap-ms = <{rec['quick_tap']}>;")
            if "prior_idle" in rec:
                print(f"    require-prior-idle-ms = <{rec['prior_idle']}>;")
            print(f"    flavor = \"{rec.get('flavor', 'balanced')}\";")
            print(f"    bindings = <&kp>, <&kp>;")
            print(f"  }};")

        print("};\n")

        print("\n// Example usage in your keymap:")
        if 'j' in recommendations:
            print(f"// For 'j' as shift when held: &hrm_j LSHIFT J")
        if 'f' in recommendations:
            print(f"// For 'f' as shift when held: &hrm_f RSHIFT F")
        if 'SPACE' in recommendations:
            print(f"// For space with layer tap: &hrm_SPACE LAYER_NUM SPACE")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze HRM timing for 'f', 'j', and 'SPACE' keys."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include detailed explanations"
    )
    args = parser.parse_args()

    print("\n" + "="*80)
    print("  HRM TIMING ANALYSIS")
    print("="*80)
    print("\n📊 This analysis is TIMING-BASED ONLY")
    print("   We measure how long you hold keys and time between presses.")
    print("   Typos, spelling errors, and what you typed don't matter!\n")

    analyzer = HRMAnalyzer()

    print("Loading keyboard logs...")
    analyzer.load_logs()

    if not analyzer.key_events:
        print("No keyboard log data found!")
        print("Please run 'python main.py start' first and type the test script.")
        return

    print(f"Loaded {len(analyzer.key_events)} keyboard events")

    print("Analyzing HRM patterns...")
    analyzer.analyze_events()

    analyzer.print_statistics()
    recommendations = analyzer.calculate_recommendations()
    analyzer.generate_zmk_config(recommendations)

    print("\n" + "="*80)
    print("KEY INSIGHTS & NEXT STEPS")
    print("="*80)
    print("""
1. Review the statistics above to understand your typing patterns
2. Look for overlaps between tap and hold times (warnings above)
3. Copy the ZMK config to your keymap file
4. Test the new settings and iterate:
   - If you get accidental capitals: INCREASE tapping-term-ms
   - If shift feels slow to activate: DECREASE tapping-term-ms
   - If you get activation during rolls: INCREASE require-prior-idle-ms
   - If normal taps feel delayed: DECREASE quick-tap-ms

5. Consider using different flavors:
   - "tap-preferred": Favors tapping (good for high-frequency letters)
   - "balanced": Balanced between tap and hold
   - "hold-preferred": Favors holding (good for dedicated modifiers)

6. For space-based quotes (space+m/n), consider:
   - Using a separate layer with quote keys instead of hold-tap
   - OR using a longer tapping-term-ms for space (200-300ms)
    """)


if __name__ == "__main__":
    main()
