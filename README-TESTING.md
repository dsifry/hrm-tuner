# HRM Timing Test - Quick Reference

## 🚀 Quick Start

```bash
./quick-start.sh
```

That's it! The script will guide you through everything.

## 📝 Manual Steps

1. **Start logging:**
   ```bash
   python main.py start
   ```

2. **Open test script in another window:**
   ```bash
   cat TYPING-SCRIPT-HRM
   # or
   open TYPING-SCRIPT-HRM
   ```

3. **Type through all 12 sections**
   - Type at YOUR normal speed
   - **TYPOS ARE FINE!** We only measure timing!
   - Focus on Part 12 (flow state challenge) - type it FAST!

4. **Stop logging:**
   - Press `Control-C`

5. **Analyze:**
   ```bash
   python hrmAnalysis.py --verbose
   ```

## ⚠️ IMPORTANT

### ✅ DO:
- Type at your normal/fast speed
- Make mistakes - they show where HRMs fail!
- Type Part 12 really fast (flow state challenge)
- Use your HRMs as you intend (even if they don't work yet)

### ❌ DON'T:
- Slow down for accuracy
- Pause to fix typos
- Worry about spelling
- Try to type perfectly

## 🎯 What We Measure

**We measure:**
- Key hold durations (milliseconds)
- Time between keypresses
- Tap vs hold patterns

**We ignore:**
- What you typed
- Spelling/grammar
- Typos and errors

## 📊 Example Output

```
Key: 'j'
─────────────────────────────────────────

PURE TAPS (normal typing):
  Average: 87.3ms
  95th percentile: 142.8ms  ← Your longest tap

HRM HOLDS (used as shift):
  Average: 178.4ms
  Min: 134.2ms  ← Your shortest hold

Recommendations:
  tapping-term-ms = 160
  flavor = "balanced"
```

## 🔧 What You'll Get

1. **Detailed timing statistics** for f, j, and space
2. **Overlap analysis** showing where tap/hold conflict
3. **ZMK config** ready to copy into your keymap
4. **Specific recommendations** based on YOUR typing

## 📚 More Info

- **TYPING-INSTRUCTIONS.md** - Detailed explanation of why typos don't matter
- **ANALYSIS-PLAN.md** - Full technical details and theory
- **TYPING-SCRIPT-HRM** - The actual test script

## 🎹 Expected Results

Based on your current settings (220ms threshold), we expect to recommend:
- Lower tapping-term-ms (140-170ms range)
- Change to "balanced" flavor
- Adjust require-prior-idle-ms (80-120ms)

This should fix:
- "jgood" not becoming "Good"
- Space+m and space+n timing issues
- Accidental activations during rolls

## ❓ Questions?

**Q: What if I mess up a lot?**
A: Perfect! That shows us where the timing fails.

**Q: Should I redo it?**
A: Only if you typed WAY slower than normal. Otherwise, mistakes are data!

**Q: How accurate should I be?**
A: Not at all! Type like you're in flow.

**Q: What if my HRMs don't work during the test?**
A: That's EXACTLY what we want to see! Type what actually happens.

---

**Ready to start?** Run `./quick-start.sh`
