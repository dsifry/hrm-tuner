# Home Row Modifier Troubleshooting Guide

A practical guide to diagnosing and fixing timing issues with Home Row Modifiers (HRM), based on real-world experience tuning a ZMK keyboard.

## Table of Contents
- [Common HRM Problems](#common-hrom-problems)
- [Understanding the Key Parameters](#understanding-the-key-parameters)
- [Diagnostic Process](#diagnostic-process)
- [Case Study: Fixing Dropped Letters](#case-study-fixing-dropped-letters)
- [Analyzing Your Typing Data](#analyzing-your-typing-data)
- [Parameter Tuning Guide](#parameter-tuning-guide)
- [Testing Your Changes](#testing-your-changes)

---

## Common HRM Problems

### Problem 1: Dropped Letters After Pauses
**Symptom:** When you start typing a word after a pause, the first letter disappears.
- "flow" becomes "low"
- "japan" becomes "apan"
- "finish" becomes "inish"

**Key observation:** This ONLY happens after pauses, not mid-word. "infinity" works fine (note the "fi" in the middle).

### Problem 2: False Shift Activation (Unwanted Capitals)
**Symptom:** Letters get capitalized when you don't want them to.
- "flow" becomes "Low"
- "full" becomes "Ull"
- "japan" becomes "Apan"

**Key observation:** This happens because your fingers naturally overlap slightly when typing fast - you're still holding the HRM key when you press the next key.

### Problem 3: Shift Won't Activate When You Want It
**Symptom:** When trying to use the HRM as a modifier, it types the letter instead.
- Trying to type "Flow" (hold f, press l) → types "fl" or "flow"
- The hold time threshold is too long for comfortable use

---

## Understanding the Key Parameters

HRM behavior is controlled by several timing parameters in ZMK:

### `tapping-term-ms` (HOLDING_TIME)
**What it does:** How long you must hold a key before it's considered a "hold" (modifier) vs a "tap" (letter).

**Typical values:** 150-280ms
- **Too low (< 150ms):** False modifier activation on fast typing
- **Too high (> 300ms):** Hard to activate modifiers intentionally
- **Sweet spot:** 200-240ms for most typists

### `require-prior-idle-ms` (STREAK_DECAY)
**What it does:** How long the keyboard must be idle before the key enters "wait and see" mode.

**Typical values:** 0-175ms
- **0 (disabled):** Key always responds immediately based on hold duration alone
- **100-150ms:** After this much idle time, keyboard waits `tapping-term-ms` to decide tap vs hold
- **Problem:** If set too low, causes dropped letters when starting words after pauses

**Example of the problem:**
1. You pause typing for 200ms (thinking)
2. You press 'f' to start "flow"
3. `require-prior-idle-ms` = 100ms was exceeded
4. Keyboard enters "wait and see" mode, waits full `tapping-term-ms` (150ms)
5. If you release 'f' before 150ms, it might not register in time
6. Result: "low" instead of "flow"

### `quick-tap-ms` (REPEAT_DECAY)
**What it does:** If you tap the same key twice within this time, the second tap is always a tap (for key repeat).

**Typical values:** 200-350ms
- Allows double-tapping home row keys for repeat (like 'ff' in 'offline')

### `flavor`
**What it does:** Determines how the keyboard decides between tap and hold.

**Options:**
- **`"tap-preferred"`:** Always produces tap on release, UNLESS another key was pressed while holding
  - ✅ Good if you rarely use the modifier
  - ❌ Bad if you have keystroke overlap (fast rolling typing)

- **`"balanced"`:** Decides based on timing and context
  - ✅ Tolerates some keystroke overlap
  - ✅ More predictable behavior
  - ⚠️ Requires proper `tapping-term-ms` tuning

- **`"hold-preferred"`:** Biased toward modifier activation
  - ❌ Usually too aggressive for home row keys

### `hold-trigger-on-release`
**What it does:** Delays the decision until you release the key (allows waiting for other home row mods).

**Effect:** Makes the system look at release timing patterns, not just hold duration. Can cause false triggers if you have natural keystroke overlap.

---

## Diagnostic Process

### Step 1: Identify Your Problem Pattern

Type these test words and note what happens:

**After a pause (test for Problem 1):**
```
flow
japan
finish
from
```

**At normal speed (test for Problem 2):**
```
flow flaw full finish from flatulence
japan jazz jewel jersey just jump
```

**Intentional capitals (test for Problem 3):**
```
Flow From Finish (hold f + first letter)
Japan Jazz Jewel (hold j + first letter)
```

### Step 2: Collect Keystroke Data

Understanding your natural typing rhythm is crucial. You need to know:
1. How long do you naturally hold keys? (typical: 80-120ms)
2. Do your keypresses overlap? (fast typists: yes, 10-30ms overlap)
3. What's your pause duration between words? (typical: 200-500ms)

**Method:** Use a keystroke logger to capture raw timing data.

Example Python script (see `analyze_overlap.py` in this repo):
- Logs all keypress and release events with timestamps
- Analyzes cross-hand rolls (f→right-hand, j→left-hand)
- Calculates overlap duration and frequency

### Step 3: Analyze the Data

Look for these patterns in your data:

**Cross-hand roll overlap analysis:**
```
Key 'f' (cross-hand rolls):
  Total presses: 213
  Cross-hand overlaps: 43
  Overlap rate: 20.2%
  Average overlap: 24.2ms

Key 'j' (cross-hand rolls):
  Total presses: 98
  Cross-hand overlaps: 7
  Overlap rate: 7.1%
  Average overlap: 10.1ms
```

**Key insights from this data:**
- 20% overlap rate means 1 in 5 times you type 'f', you're still holding it when the next key presses
- Average 24ms overlap is well under typical 150ms `tapping-term-ms`
- BUT: With "tap-preferred" flavor, ANY overlap triggers modifier
- With "balanced" + `hold-trigger-on-release`, overlap detection still happens

---

## Case Study: Fixing Dropped Letters

### Initial Problem
- "flow" → "low"
- "japan" → "apan"
- Only after pauses, not mid-word

### Initial Configuration
```c
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_STREAK_DECAY (TAPPING_RESOLUTION - 100)  // 100ms
#define INDEX_HOLDING_TIME (TAPPING_RESOLUTION - 50)   // 150ms
```

### Root Cause Analysis

**Why letters dropped after pauses:**
1. User pauses for 200ms+ between words
2. `require-prior-idle-ms = 100ms` was exceeded
3. Keyboard enters "wait and see" mode for next key press
4. When 'f' is pressed, keyboard waits up to 150ms to decide tap vs hold
5. User's natural 'f' tap is ~90ms
6. Timing is close to threshold → sometimes misses the tap

**Why it worked mid-word:**
1. When typing "infinity", user just pressed 'n' < 100ms ago
2. `require-prior-idle-ms` not exceeded
3. 'f' registers immediately as tap
4. No delay, no problem

### First Attempted Fix (WRONG)
```c
#define INDEX_HOLDING_TYPE "tap-preferred"  // WRONG for this typing style
#define INDEX_STREAK_DECAY (TAPPING_RESOLUTION - 25)  // 175ms
```

**Why this failed:**
- "tap-preferred" triggers modifier on ANY overlap
- User has 20% overlap rate with 24ms average
- Result: "flow" → "Low" (false shift activation)

### Discovery: Keystroke Overlap Analysis

Ran keystroke logger and analyzer, discovered:
```
Example f→l rolls:
f→l: overlap=33.8ms, f_held=94.0ms
f→l: overlap=16.5ms, f_held=106.1ms
f→i: overlap=14.4ms, f_held=14.7ms
f→o: overlap=13.1ms, f_held=14.2ms

Most common patterns:
f→i: 19 times (finish, infinity, fiji)
f→o: 14 times (flow, from, for)
f→l: 9 times (flow, flaw, fling)
```

**Key insight:** User has natural rolling overlap. "tap-preferred" won't work.

### Correct Fix

```c
#define INDEX_HOLDING_TYPE "balanced"           // Tolerates overlap
#define INDEX_STREAK_DECAY 0                    // Disable idle timeout
#define INDEX_HOLDING_TIME (TAPPING_RESOLUTION + 40)  // 240ms
```

**Why this works:**

1. **`INDEX_STREAK_DECAY = 0`** (disabled `require-prior-idle-ms`)
   - No more "wait and see" mode after pauses
   - Key always responds based on hold duration alone
   - Fixes the dropped letters after pause problem

2. **`INDEX_HOLDING_TYPE = "balanced"`**
   - Tolerates natural keystroke overlap
   - Won't trigger modifier on 10-30ms overlaps
   - Requires hold duration to exceed `tapping-term-ms`

3. **`INDEX_HOLDING_TIME = 240ms`** (increased from 150ms)
   - User's natural holds: ~90-105ms
   - User's overlap: ~24ms average
   - 240ms threshold is safely above natural typing
   - Still comfortable for intentional modifier use

### Results After Fix

**Normal typing (no false triggers):**
```
✅ flow flaw full finish from flatulence
✅ japan jazz jewel jersey just jump
```

**Intentional capitals (reliable activation):**
```
✅ Flow From Finish Query Water Ready
✅ Amazing Wonderful Great Quest Expert
```

**Problem solved!**

---

## Analyzing Your Typing Data

### Setting Up Keystroke Logging

**Option 1: Python with pynput**
```python
from pynput import keyboard
import time
import json

events = []

def on_press(key):
    events.append({
        'timestamp': time.time(),
        'button': str(key),
        'is_on_press': True
    })

def on_release(key):
    events.append({
        'timestamp': time.time(),
        'button': str(key),
        'is_on_press': False
    })

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
```

### Analyzing Cross-Hand Rolls

Focus on these patterns:
- **f + right-hand keys** (i, o, l, u, y, h, j, k, p, n, m)
- **j + left-hand keys** (a, s, d, f, g, q, w, e, r, t, z, x, c, v, b)

These are where HRM conflicts happen.

### Key Metrics to Calculate

1. **Overlap Rate:** What percentage of HRM presses have overlap?
   - < 5%: "tap-preferred" might work
   - 5-15%: Use "balanced" with tuned timing
   - > 15%: Definitely need "balanced" with longer `tapping-term-ms`

2. **Average Overlap Duration:** How long is the overlap?
   - < 10ms: Minimal, easy to handle
   - 10-30ms: Common for fast typists
   - > 30ms: Very aggressive rolling style

3. **Natural Hold Duration:** How long do you hold keys normally?
   - Fast: 60-80ms
   - Average: 80-120ms
   - Slower: 120-180ms

4. **Pause Duration Between Words:** How long do you pause?
   - No pauses: < 100ms (very fast typing)
   - Normal: 200-500ms
   - Thinking: 500ms+

### Setting Your Thresholds

**`tapping-term-ms` should be:**
- Greater than: (max natural hold duration) + (avg overlap)
- Less than: Your comfortable deliberate hold time
- Formula: `tapping-term-ms = natural_hold + overlap + safety_margin`

**Example calculation:**
```
Natural hold: 105ms (max observed)
Overlap: 24ms (average)
Safety margin: 100ms
Result: 105 + 24 + 100 = 229ms → round to 240ms
```

**`require-prior-idle-ms` should be:**
- 0 if you have dropped letter problems
- 100-150ms if you want faster modifier activation during continuous typing
- Higher values make modifiers respond faster mid-typing but cause issues after pauses

---

## Parameter Tuning Guide

### Conservative Starting Point (Recommended)
```c
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_HOLDING_TIME 240
#define INDEX_STREAK_DECAY 0
#define INDEX_REPEAT_DECAY 350
```

**Good for:**
- Typists with natural overlap
- Those who get false capitals
- People who use HRM modifiers occasionally

### Aggressive (Fast Modifier Activation)
```c
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_HOLDING_TIME 180
#define INDEX_STREAK_DECAY 150
#define INDEX_REPEAT_DECAY 300
```

**Good for:**
- Very clean, deliberate typists
- Those who frequently use HRM modifiers
- Minimal keystroke overlap

**Risk:** May cause false capitals if you type with overlap

### Tap-Focused (Rarely Use Modifiers)
```c
#define INDEX_HOLDING_TYPE "tap-preferred"
#define INDEX_HOLDING_TIME 200
#define INDEX_STREAK_DECAY 0
#define INDEX_REPEAT_DECAY 350
```

**Good for:**
- Typists with NO keystroke overlap
- Those who rarely/never use HRM modifiers
- Very sequential typing style (one key fully released before next pressed)

**Risk:** Any overlap will trigger modifier

---

## Testing Your Changes

### Test Suite

After changing parameters, run through this complete test:

#### Test 1: Normal Typing (Should NOT Capitalize)
```
Type these after a 2-3 second pause:

flow flaw full finish from fjord first
japan jazz jewel jersey just jump jest
```

**Expected:** All lowercase
**If capitals appear:** `tapping-term-ms` too low OR flavor is "tap-preferred" with overlap

#### Test 2: Mid-Word Typing (Should Work Smoothly)
```
Type at normal speed:

infinity unofficial waffle raffle baffle
nonjewish prejudice trajectory
```

**Expected:** Smooth typing, no issues
**If problems:** Adjust `quick-tap-ms` for better repeat handling

#### Test 3: Intentional Capitals (Should Capitalize)
```
Hold f/j and press the target key:

Flow From Finish First Full (f + right hand)
Japan Jazz Jewel Jersey Just (j + left hand)
Query Water Ready Top (j + top row)
```

**Expected:** All capitalized
**If lowercase appears:** `tapping-term-ms` too high, hard to activate

#### Test 4: Top Row Reaches (Challenging)
```
Intentional capitals with top row:

Query Water Eager Ready Trouble
```

**Expected:** All capitalized
**Why harder:** Finger travel to top row may shorten hold time

#### Test 5: Rapid Words (Stress Test)
```
Type this sentence quickly:

Just jump over the jersey barrier and grab the good waffle from the fjord.
```

**Expected:** No capitals, smooth typing
**If issues:** May need to increase `tapping-term-ms`

### Interpreting Test Results

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Dropped letters after pause | `require-prior-idle-ms` too low | Set to 0 or increase `tapping-term-ms` |
| False capitals on normal typing | `tapping-term-ms` too low OR "tap-preferred" with overlap | Increase to 240ms, use "balanced" |
| Can't activate shift | `tapping-term-ms` too high | Decrease to 200-220ms |
| Top row capitals fail | Hold time shortened by reach | Practice or decrease `tapping-term-ms` slightly |
| Mid-word issues | `quick-tap-ms` too low | Increase to 300-350ms |

---

## Advanced Topics

### Understanding hold-trigger-on-release

This setting makes the keyboard wait for you to release the key before deciding tap vs hold. It's designed to work with other home row mods.

**Interaction with overlap:**
- Even if hold duration < `tapping-term-ms`, overlap can trigger modifier
- With "balanced" flavor, reduces but doesn't eliminate false triggers
- This is why `tapping-term-ms` needs to be well above your natural hold + overlap time

### Flavor Behavior Summary

**"tap-preferred":**
```
Press f, release after 50ms → 'f'
Press f, hold 200ms, release → 'f' (still tap!)
Press f, press l while holding → 'L' (modifier activated)
```
Decision: Based on "was another key pressed while holding?"

**"balanced":**
```
Press f, release after 50ms → 'f'
Press f, hold 250ms, release → modifier (held too long)
Press f, press l after 10ms overlap → depends on total hold time
  - If total hold < tapping-term-ms: usually 'f' then 'l'
  - If total hold > tapping-term-ms: modifier activated
```
Decision: Based on hold duration and context

**"hold-preferred":**
```
Press f, release after 50ms → usually modifier
Press f, quick tap → tap (only if very quick)
```
Decision: Biased toward modifier
⚠️ Usually too aggressive for home row letters

### Per-Finger Customization

You can set different values for each finger:

```c
// Faster modifiers for middle fingers
#define LEFT_MIDDY_HOLDING_TIME 200
#define RIGHT_MIDDY_HOLDING_TIME 200

// Slower for index (used more as letters)
#define LEFT_INDEX_HOLDING_TIME 240
#define RIGHT_INDEX_HOLDING_TIME 240

// Pinkies rarely used as modifiers
#define LEFT_PINKY_HOLDING_TIME 280
#define RIGHT_PINKY_HOLDING_TIME 280
```

This lets you optimize each finger for its usage pattern.

---

## Troubleshooting Checklist

- [ ] Collected keystroke timing data
- [ ] Calculated overlap rate and average overlap duration
- [ ] Identified natural hold duration
- [ ] Set `tapping-term-ms` > (natural_hold + overlap + 100ms)
- [ ] Set `require-prior-idle-ms = 0` if having dropped letter issues
- [ ] Using "balanced" flavor if overlap rate > 5%
- [ ] Tested all scenarios: normal typing, after pause, intentional capitals
- [ ] Verified top row reaches work
- [ ] Confirmed no false capitals at normal typing speed

---

## Quick Reference

### Common Configurations

**Problem: Dropped letters after pause**
```c
#define INDEX_STREAK_DECAY 0  // Disable idle timeout
```

**Problem: False capitals on fast typing**
```c
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_HOLDING_TIME 240  // Increase threshold
```

**Problem: Can't activate modifier**
```c
#define INDEX_HOLDING_TIME 200  // Decrease threshold
```

**Problem: All of the above (the sweet spot)**
```c
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_HOLDING_TIME 240
#define INDEX_STREAK_DECAY 0
#define INDEX_REPEAT_DECAY 350
```

---

## Summary

Home Row Modifiers require careful tuning to match your natural typing rhythm. The key is:

1. **Understand your typing data** - measure your natural hold times and overlap
2. **Set thresholds appropriately** - `tapping-term-ms` must be above your natural typing
3. **Choose the right flavor** - "balanced" for most people, especially with overlap
4. **Disable idle timeout** - if you get dropped letters after pauses
5. **Test thoroughly** - use the test suite to validate your changes

The goal is to make HRM "invisible" - it should just work naturally with your existing typing style, not require you to change how you type.

---

## Additional Resources

- [ZMK Documentation: Hold-Tap Behavior](https://zmk.dev/docs/behaviors/hold-tap)
- [Urob's ZMK Config (Advanced HRM)](https://github.com/urob/zmk-config)
- Keystroke analysis tools in this repository:
  - `analyze_overlap.py` - Cross-hand roll overlap analysis
  - `keyboard_logger.py` - Raw keystroke timing capture

---

**Document Version:** 1.0
**Last Updated:** 2025-01-23
**Based on:** Real-world tuning of Glove80 keyboard with ZMK firmware
