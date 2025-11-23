# 🎯 HRM Typing Test Instructions

## TL;DR

**Type naturally and fast. Typos don't matter. We only measure timing!**

## What We're Measuring

This analysis captures:
- ⏱️ How long you hold each key
- ⏱️ Time between keypresses
- ⏱️ Difference between taps and holds

We are NOT measuring:
- ❌ Spelling
- ❌ Accuracy
- ❌ What you actually type
- ❌ Grammar or punctuation

## Why Typos Are OK

The keyboard logger records **raw timing data**:
```
Key 'j' pressed at 1000.123456 seconds
Key 'g' pressed at 1000.234567 seconds
Key 'j' released at 1000.345678 seconds
Key 'g' released at 1000.456789 seconds
```

If you meant to type "good" but typed "god" instead, we still see:
- 'g' held for ~0.22 seconds
- 'd' held for ~0.11 seconds
- Time between 'g' press and 'd' press: ~0.15 seconds

**That's all we need!** The actual letters don't matter.

## What Matters

### ✅ Type at your normal speed
This reveals your real-world timing patterns

### ✅ Use your HRMs as you intend
- When you want "Good", hold 'j' then tap 'g'
- When you want "jersey", just type normally

### ✅ Type in flow state for Part 11
This is where the issues happen, so this is the most important data!

### ✅ Include your mistakes
If you accidentally type "jgood" instead of "Good", that's PERFECT DATA!
We need to see when the HRM fails!

## What Doesn't Matter

### ❌ Spelling errors
"jefferson" or "jeferson" - both give us the timing we need

### ❌ Missing letters
"beleif" instead of "belief" - still shows your 'f' tap timing

### ❌ Extra letters
"goood" instead of "good" - extra data points are fine!

### ❌ Wrong capitalizations
If you type "good" when you meant "Good", that tells us your HRM timing needs adjustment!

## The 11 Test Sections

1. **Baseline taps** - Normal words to see regular 'f'/'j' timing
2. **j + left hand** - Intentional shift usage
3. **f + right hand** - Intentional shift usage
4. **Problematic j patterns** - The "jgood" → "Good" issue
5. **Space + m for '** - Single quote timing
6. **Space + n for "** - Double quote timing
7. **Mixed HRM** - Realistic paragraph
8. **Fast typing** - Potential conflicts
9. **Both f and j** - Using both HRMs
10. **Quote-heavy** - Multiple quote combinations
11. **Flow state** - FAST natural typing ⭐ MOST IMPORTANT!

## Tips for Best Results

1. **Don't slow down for accuracy** - Type at YOUR normal speed
2. **Don't pause to fix mistakes** - Just keep going
3. **Type Part 11 really fast** - This reveals the real issues
4. **Be natural** - Pretend you're writing a quick email

## After Typing

Press Control-C and the analysis will show:
- Your actual tap times (probably 50-120ms)
- Your actual hold times (probably 120-200ms)
- Where they overlap (the problem!)
- Exact ZMK settings to fix it

## Questions?

**"What if I make a lot of mistakes?"**
Perfect! That's data!

**"What if I can't produce the quotes with space+m/n?"**
That's exactly what we're trying to fix! Type what actually happens.

**"Should I redo it if I mess up?"**
No! Mistakes show us where the timing fails.

**"How long should this take?"**
5-10 minutes of typing. Don't rush the reading, rush the typing!

---

Ready? Run:
```bash
./quick-start.sh
```

Or manually:
```bash
python main.py start
# Type the test
# Press Control-C
python hrmAnalysis.py --verbose
```
