#!/usr/bin/env python3
"""
Analyze keystroke overlap patterns for 'f' and 'j' keys.
Version 2: Handle the fact that f/j might be interpreted as shift modifiers,
so we need to look for the PATTERN rather than the literal keys.

Looking for:
- 'f' key followed by RIGHT-HAND letter (since f+right = shift)
- 'j' key followed by LEFT-HAND letter (since j+left = shift)
- Measure the overlap between them
"""

import json
import glob
from collections import defaultdict

# Define hand positions (QWERTY layout)
LEFT_HAND = set('qwertasdfgzxcvb12345')
RIGHT_HAND = set('yuiophjkl;nm,./67890')

def analyze_rolls(log_files):
    """
    Analyze f→right-hand and j→left-hand rolls to detect overlap.
    """

    f_rolls = []  # f followed by right-hand key
    j_rolls = []  # j followed by left-hand key

    f_stats = {'count': 0, 'overlaps': 0, 'overlap_durations': [], 'next_keys': defaultdict(int)}
    j_stats = {'count': 0, 'overlaps': 0, 'overlap_durations': [], 'next_keys': defaultdict(int)}

    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
                records = data.get('records', [])

                if not records:
                    continue

                i = 0
                while i < len(records):
                    record = records[i]
                    button = record['button'].lower()
                    is_press = record['is_on_press']
                    timestamp = record['timestamp']

                    # Look for 'f' key press
                    if button == 'f' and is_press:
                        f_stats['count'] += 1

                        # Find when 'f' is released
                        f_release_time = None
                        for j in range(i + 1, min(i + 30, len(records))):
                            if records[j]['button'].lower() == 'f' and not records[j]['is_on_press']:
                                f_release_time = records[j]['timestamp']
                                break

                        if f_release_time is None:
                            i += 1
                            continue

                        # Look for next key press (should be right-hand for cross-hand roll)
                        for j in range(i + 1, min(i + 30, len(records))):
                            next_record = records[j]
                            next_button = next_record['button'].lower()

                            # Skip modifiers and the 'f' release
                            if next_button in ['shift', 'key.shift', 'ctrl', 'alt', 'cmd', 'f'] or not next_record['is_on_press']:
                                continue

                            # Check if it's a right-hand key (cross-hand roll)
                            if any(char in RIGHT_HAND for char in next_button):
                                next_press_time = next_record['timestamp']

                                # Calculate overlap: how long was f still held after next key pressed?
                                if next_press_time < f_release_time:
                                    overlap_ms = (f_release_time - next_press_time) * 1000
                                    f_stats['overlaps'] += 1
                                    f_stats['overlap_durations'].append(overlap_ms)
                                    f_stats['next_keys'][next_button] += 1

                                    f_rolls.append({
                                        'first_key': 'f',
                                        'next_key': next_button,
                                        'overlap_ms': overlap_ms,
                                        'f_hold_duration_ms': (f_release_time - timestamp) * 1000,
                                        'file': log_file
                                    })
                                break

                    # Look for 'j' key press
                    elif button == 'j' and is_press:
                        j_stats['count'] += 1

                        # Find when 'j' is released
                        j_release_time = None
                        for j_idx in range(i + 1, min(i + 30, len(records))):
                            if records[j_idx]['button'].lower() == 'j' and not records[j_idx]['is_on_press']:
                                j_release_time = records[j_idx]['timestamp']
                                break

                        if j_release_time is None:
                            i += 1
                            continue

                        # Look for next key press (should be left-hand for cross-hand roll)
                        for j_idx in range(i + 1, min(i + 30, len(records))):
                            next_record = records[j_idx]
                            next_button = next_record['button'].lower()

                            # Skip modifiers and the 'j' release
                            if next_button in ['shift', 'key.shift', 'ctrl', 'alt', 'cmd', 'j'] or not next_record['is_on_press']:
                                continue

                            # Check if it's a left-hand key (cross-hand roll)
                            if any(char in LEFT_HAND for char in next_button):
                                next_press_time = next_record['timestamp']

                                # Calculate overlap
                                if next_press_time < j_release_time:
                                    overlap_ms = (j_release_time - next_press_time) * 1000
                                    j_stats['overlaps'] += 1
                                    j_stats['overlap_durations'].append(overlap_ms)
                                    j_stats['next_keys'][next_button] += 1

                                    j_rolls.append({
                                        'first_key': 'j',
                                        'next_key': next_button,
                                        'overlap_ms': overlap_ms,
                                        'j_hold_duration_ms': (j_release_time - timestamp) * 1000,
                                        'file': log_file
                                    })
                                break

                    i += 1

        except Exception as e:
            print(f"Error processing {log_file}: {e}")
            continue

    return f_rolls, j_rolls, f_stats, j_stats

def print_stats(key_name, stats, rolls):
    """Print statistics for a given key."""
    if stats['count'] == 0:
        print(f"No '{key_name}' key presses found.")
        return

    overlap_rate = (stats['overlaps'] / stats['count']) * 100
    print(f"Key '{key_name}' (cross-hand rolls):")
    print(f"  Total presses: {stats['count']}")
    print(f"  Cross-hand overlaps: {stats['overlaps']}")
    print(f"  Overlap rate: {overlap_rate:.1f}%")

    if stats['overlap_durations']:
        durations = stats['overlap_durations']
        avg = sum(durations) / len(durations)
        print(f"  Average overlap: {avg:.1f}ms")
        print(f"  Min overlap: {min(durations):.1f}ms")
        print(f"  Max overlap: {max(durations):.1f}ms")

        # Distribution
        ranges = [(0, 10), (10, 20), (20, 30), (30, 50), (50, 100), (100, float('inf'))]
        print(f"  Overlap distribution:")
        for start, end in ranges:
            count = sum(1 for d in durations if start <= d < end)
            if count > 0:
                end_str = f"{end}ms" if end != float('inf') else "ms+"
                print(f"    {start}-{end_str}: {count} occurrences")

        # Most common next keys
        print(f"  Most common next keys:")
        for key, count in sorted(stats['next_keys'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {key_name}→{key}: {count} times")

    print()

def main():
    log_files = sorted(glob.glob('/Users/dsifry/Developer/hrm-tuner/log/*.json'))

    print(f"Analyzing {len(log_files)} log files...\n")

    f_rolls, j_rolls, f_stats, j_stats = analyze_rolls(log_files)

    print("=" * 70)
    print("CROSS-HAND ROLL ANALYSIS (f→right, j→left)")
    print("=" * 70)
    print()

    print_stats('f', f_stats, f_rolls)
    print_stats('j', j_stats, j_rolls)

    # Show examples
    if f_rolls:
        print("=" * 70)
        print("EXAMPLE 'f' CROSS-HAND ROLLS (first 20):")
        print("=" * 70)
        for roll in f_rolls[:20]:
            print(f"f→{roll['next_key']}: overlap={roll['overlap_ms']:.1f}ms, f_held={roll['f_hold_duration_ms']:.1f}ms")
        print()

    if j_rolls:
        print("=" * 70)
        print("EXAMPLE 'j' CROSS-HAND ROLLS (first 20):")
        print("=" * 70)
        for roll in j_rolls[:20]:
            print(f"j→{roll['next_key']}: overlap={roll['overlap_ms']:.1f}ms, j_held={roll['j_hold_duration_ms']:.1f}ms")
        print()

    # Conclusion
    print("=" * 70)
    print("INTERPRETATION:")
    print("=" * 70)
    print()
    print("These cross-hand rolls (f→right, j→left) are where HRM conflicts occur.")
    print("If overlap exists, the keyboard might interpret it as 'shift + key'.")
    print()

    if f_stats['overlaps'] > 0 or j_stats['overlaps'] > 0:
        avg_overlap = 0
        total_overlaps = 0
        if f_stats['overlap_durations']:
            avg_overlap += sum(f_stats['overlap_durations'])
            total_overlaps += len(f_stats['overlap_durations'])
        if j_stats['overlap_durations']:
            avg_overlap += sum(j_stats['overlap_durations'])
            total_overlaps += len(j_stats['overlap_durations'])

        if total_overlaps > 0:
            avg_overlap /= total_overlaps
            print(f"Average cross-hand overlap: {avg_overlap:.1f}ms")
            print()
            print("Recommendations:")
            print(f"1. Keep 'balanced' flavor (NOT 'tap-preferred')")
            print(f"2. Set require-prior-idle-ms = 0 (disable idle timeout)")
            print(f"3. Ensure tapping-term-ms > {avg_overlap + 20:.0f}ms to avoid false shift triggers")
            print(f"   (Current setting: 150ms should be fine)")

if __name__ == '__main__':
    main()
