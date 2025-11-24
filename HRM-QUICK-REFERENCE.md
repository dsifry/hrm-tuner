# HRM Quick Reference Card

Fast reference for diagnosing and fixing Home Row Modifier timing issues.

## Problem Diagnosis

| Symptom | Problem | Quick Fix |
|---------|---------|-----------|
| "flow" → "low" after pause | Dropped letter | `INDEX_STREAK_DECAY = 0` |
| "flow" → "Low" when typing fast | False shift | Increase `INDEX_HOLDING_TIME` to 240ms |
| Hold f+l doesn't capitalize | Can't activate shift | Decrease `INDEX_HOLDING_TIME` to 200ms |
| Works mid-word, fails at start | Idle timeout issue | `INDEX_STREAK_DECAY = 0` |
| Random capitals when rolling | Keystroke overlap | Use "balanced" flavor + higher timing |

## Parameter Quick Guide

### tapping-term-ms (HOLDING_TIME)
How long to hold before it's a modifier vs letter.

- **150ms** = Very responsive, risk false triggers
- **240ms** = Sweet spot for most typists
- **280ms** = Conservative, prevents false triggers
- **Formula:** `natural_hold + overlap + 100ms`

### require-prior-idle-ms (STREAK_DECAY)
How long keyboard must be idle before "wait and see" mode.

- **0** = Disabled (recommended if dropped letters)
- **100ms** = Faster modifier mid-typing
- **150ms** = Aggressive (may drop letters)

### flavor
How keyboard decides tap vs hold.

- **"tap-preferred"** = Only for NO overlap typists
- **"balanced"** = Best for most people ✅
- **"hold-preferred"** = Too aggressive for letters

## Recommended Starting Config

```c
// Conservative, works for most typists
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_HOLDING_TIME 240
#define INDEX_STREAK_DECAY 0
#define INDEX_REPEAT_DECAY 350
```

## Test Words

### Test After Pause (dropped letters?)
```
flow japan finish from just
```

### Test Fast Typing (false capitals?)
```
flow flaw full finish flatulence
japan jazz jewel jersey jump
```

### Test Shift Activation (capitals work?)
```
Flow From Finish (hold f + letter)
Japan Jazz Jewel (hold j + letter)
```

## Tuning Process

1. **Measure your typing:**
   - Run keystroke logger
   - Find natural hold time (usually 80-120ms)
   - Find overlap rate and duration

2. **Calculate threshold:**
   ```
   tapping-term-ms = max_hold + avg_overlap + 100
   Example: 105 + 24 + 100 = 229 → use 240ms
   ```

3. **Set parameters:**
   - Use "balanced" if overlap > 5%
   - Set STREAK_DECAY = 0 if dropped letters
   - Set HOLDING_TIME per calculation

4. **Test thoroughly:**
   - Normal typing (no capitals)
   - After pause (no dropped letters)
   - Intentional capitals (works)

## Common Mistakes

❌ Using "tap-preferred" with keystroke overlap
❌ Setting HOLDING_TIME too low (< natural typing)
❌ Forgetting to test after pauses
❌ Not measuring actual typing data first

## When to Adjust

**Increase HOLDING_TIME if:**
- Getting false capitals on normal typing
- Seeing unwanted modifiers

**Decrease HOLDING_TIME if:**
- Can't activate shift reliably
- Hold feels too long

**Set STREAK_DECAY = 0 if:**
- Letters drop after pausing
- First letter of words disappears

**Use "balanced" flavor if:**
- You have ANY keystroke overlap (most people)
- Getting false triggers with "tap-preferred"

## Typical Typing Data

**Fast typist:**
- Hold: 60-80ms
- Overlap: 20-40ms
- Recommended: HOLDING_TIME = 240ms

**Average typist:**
- Hold: 80-120ms
- Overlap: 10-30ms
- Recommended: HOLDING_TIME = 240ms

**Deliberate typist:**
- Hold: 120-180ms
- Overlap: 0-10ms
- Recommended: HOLDING_TIME = 200-220ms

## Emergency Reset

If everything is broken:

```c
// Safe defaults
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_HOLDING_TIME 280
#define INDEX_STREAK_DECAY 0
#define INDEX_REPEAT_DECAY 350
```

Then tune down HOLDING_TIME gradually (260 → 240 → 220) until shift activation feels right.

---

**For full details, see:** HRM-TROUBLESHOOTING-GUIDE.md
