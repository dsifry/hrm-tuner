# HRM Timing Analysis Plan for Dave's Glove80

## Current Problem Summary

You're experiencing two main timing issues:

1. **'j' and 'f' as shift modifiers**: When typing fast (in flow), typing "jgood" doesn't capitalize to "Good" - it stays as "jgood"
2. **Space+m for `'` and space+n for `"`**: Having timing issues with these combinations

## Your Current ZMK Settings

From `daves-current-zmk.keymap`:

```c
#define TAPPING_RESOLUTION 200          // Base timing
#define INDEX_HOLDING_TIME 220          // f and j (200 + 20)
#define INDEX_HOLDING_TYPE "tap-preferred"
#define INDEX_STREAK_DECAY 150          // require-prior-idle-ms
#define INDEX_REPEAT_DECAY 350          // quick-tap-ms

#define SPACE_HOLDING_TIME 220          // Space key (200 + 20)
#define SPACE_HOLDING_TYPE "balanced"
#define SPACE_REPEAT_DECAY 200          // quick-tap-ms
```

## Why "jgood" Isn't Becoming "Good"

Based on your description and settings, here's what's happening:

1. You type 'j' quickly (want it to be shift)
2. You type 'g' while or shortly after 'j' is pressed
3. **BUT** you're releasing 'j' before 220ms expires
4. With "tap-preferred" flavor, the system sees: "Released before 220ms = regular tap = 'j'"
5. Result: "jgood" instead of "Good"

### The Critical Insight

The problem is that `tapping-term-ms = 220ms` is **too long** for your fast typing. When you're in flow:
- Your actual tap time for regular 'j': probably 50-100ms
- Your intended hold for shift: probably 100-150ms
- Current threshold: 220ms (too high!)

### Solutions to Test

After analyzing your typing data, we'll likely recommend:

1. **Lower tapping-term-ms**: Probably to 140-170ms range
   - This allows faster shift activation
   - Still above your normal tap times

2. **Adjust require-prior-idle-ms**: Currently 150ms
   - This prevents "jersey" from becoming "jeRsey"
   - Might need to lower to 80-120ms for flow typing

3. **Consider "balanced" instead of "tap-preferred"**:
   - "tap-preferred": Must release modifier for it to work
   - "balanced": Activates modifier as soon as next key is pressed (even if modifier still held)
   - For shift keys, "balanced" often works better!

4. **Add hold-trigger-key-positions**:
   - Limit 'j' shift to only activate with LEFT hand keys
   - Limit 'f' shift to only activate with RIGHT hand keys
   - This prevents accidental activation during normal typing

## Space + m/n Issues

For space+m (`'`) and space+n (`"`), the issue is likely:

1. Current `SPACE_HOLDING_TIME = 220ms` might be too long
2. OR you're not holding space long enough
3. OR the combination is conflicting with normal space typing

Possible solutions:
- Lower space holding time to 150-180ms
- Use a different mechanism (layer with dedicated quote keys)
- Add positional hold-tap to only activate quotes with m/n

## The Testing Process

### Step 1: Capture Your Typing Data

```bash
python3 main.py start
```

Then type through `TYPING-SCRIPT-HRM` naturally.

**IMPORTANT: Type at your normal speed! Typos and errors are completely fine!**
The analysis only looks at timing patterns (how long you hold keys, time between keypresses),
NOT what you actually type. Spelling mistakes don't matter at all!

The script includes:
- Normal words with f/j (baseline taps)
- Intentional shift usage (HRM holds)
- Problematic patterns ("jgood", "jersey")
- Quote combinations
- Fast "flow state" typing

Press Control-C when done.

### Step 2: Analyze the Data

```bash
python3 hrmAnalysis.py --verbose
```

This will show you:
- **Pure taps**: How long you hold f/j/space when typing normally
- **HRM holds**: How long you hold when using as modifiers
- **Activation timing**: Time from key down to next key press
- **Overlaps**: Where tap and hold times conflict (the problem area!)

### Step 3: Review Recommendations

The script will generate:
- Exact timing values based on YOUR typing
- ZMK config ready to copy-paste
- Warnings about any overlapping patterns

### Step 4: Key Metrics to Look For

After analysis, we'll focus on these critical measurements:

For 'f' and 'j':
- **Max pure tap time**: Your longest normal tap (probably 80-120ms)
- **Min HRM hold time**: Your shortest intentional shift hold (probably 120-180ms)
- **Gap between them**: Ideally 30-50ms+ separation
- **95th percentile activation time**: How fast you press the next key after holding j/f

For space:
- Same metrics, but looking at space+m and space+n patterns

## Expected Recommendations

Based on typical fast typists and your current settings being "too slow", I expect we'll recommend:

```c
// For f and j (index fingers)
#define INDEX_HOLDING_TIME 160          // Down from 220ms
#define INDEX_STREAK_DECAY 100          // Down from 150ms
#define INDEX_HOLDING_TYPE "balanced"   // Changed from "tap-preferred"

// For space
#define SPACE_HOLDING_TIME 180          // Down from 220ms
#define SPACE_REPEAT_DECAY 150          // Down from 200ms
```

But we won't know for sure until we see YOUR actual data!

## Advanced: Bilateral Hold-Tap

You already have `#define ENFORCE_BILATERAL` enabled. This is GOOD for your use case!

We can take it further with `hold-trigger-key-positions`:

```
// For 'j' - only activate shift with LEFT hand keys
left_index: left_index {
  compatible = "zmk,behavior-hold-tap";
  flavor = "balanced";
  tapping-term-ms = <160>;
  require-prior-idle-ms = <100>;
  hold-trigger-key-positions = <0 1 2 3 4 ...>; // LEFT hand positions
  bindings = <&kp>, <&kp>;
};
```

This means:
- Typing "just" → 'j' is always a tap (same hand)
- Typing "jgood" → 'j' CAN be shift (different hand)
- Eliminates most accidental activations!

## Research References

Key ZMK documentation for your case:
- Hold-tap behavior: https://zmk.dev/docs/behaviors/hold-tap
- Positional hold-tap: https://zmk.dev/docs/behaviors/hold-tap#positional-hold-tap
- Sunaku's research: https://github.com/sunaku/glove80-keymaps (you're on v41, latest is v42-rc6)

Key timing parameters explained:
- `tapping-term-ms`: The decision point - tap vs hold
- `quick-tap-ms`: Allows key repeat without triggering hold
- `require-prior-idle-ms`: Prevents hold during rolls/slides
- `flavor`: How the decision is made
  - "tap-preferred": Must release modifier for hold to work
  - "balanced": Activates on next keypress
  - "hold-preferred": Favors hold behavior

## Next Steps

1. **Run the logger** and type the test script
2. **Analyze the data** to see your actual timing patterns
3. **Update your keymap** with the recommended values
4. **Test in real usage** and iterate if needed
5. **Fine-tune** based on feel

Ready to start? Run:
```bash
python3 main.py start
```

Then open `TYPING-SCRIPT-HRM` and start typing!
