# HRM Tuner

**A data-driven typing analysis tool for optimizing Home Row Modifiers (HRMs) on ZMK keyboards.**

Tune your keyboard's timing parameters based on YOUR actual typing behavior, not generic defaults. Works with Glove80, Piantor, Corne, and any ZMK-powered keyboard.

> **Credits:** Based on [Chih-Yuan Huang's InputLogger](https://github.com/yuan64198/InputLogger), heavily modified for HRM timing analysis and modern Python environments.

---

## Table of Contents

- [What Are Home Row Modifiers?](#what-are-home-row-modifiers)
- [What This Tool Does](#what-this-tool-does)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage Workflows](#usage-workflows)
- [Understanding the Analysis](#understanding-the-analysis)
- [Applying Recommendations to ZMK](#applying-recommendations-to-zmk)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)
- [Real-World Example](#real-world-example)
- [Contributing](#contributing)
- [License](#license)
- [Additional Resources](#additional-resources)

---

## What Are Home Row Modifiers?

**Home Row Modifiers (HRMs)** let you use your home row keys (A, S, D, F, J, K, L, ;) as both regular letters AND modifier keys (Shift, Ctrl, Alt, Cmd):

- **Tap the key quickly** → Types the letter (e.g., 'f' or 'j')
- **Hold the key down** → Activates modifier (e.g., Shift)

### Why Use HRMs?

- **Ergonomic:** Eliminates reaching for modifier keys
- **Efficient:** Keeps fingers on home row
- **Powerful:** Can assign modifiers to any key, not just traditional positions

### The Challenge

Getting the timing right is critical:
- **Too fast:** Normal typing accidentally triggers modifiers → "jgood" when you meant "just good"
- **Too slow:** Intentional holds don't activate → Missing capital letters
- **Space bar issues:** Holding space for layer access accidentally triggers symbols

**This tool solves this by analyzing YOUR typing to find YOUR perfect timing.**

---

## What This Tool Does

### Core Features

1. **High-Precision Logging**
   - Records every keypress/release with microsecond timestamps
   - Captures your natural typing rhythm without interference

2. **Statistical Analysis**
   - Separates quick taps from intentional holds
   - Calculates 95th percentile for safe thresholds
   - Identifies overlapping tap/hold distributions (problem areas)

3. **Personalized Recommendations**
   - Suggests ZMK timing values based on YOUR data
   - Recommends `tapping-term-ms`, `quick-tap-ms`, `require-prior-idle-ms`
   - Provides safe margins to prevent misfires

4. **Two Analysis Modes**
   - **Simple Analysis:** Basic per-key statistics (good for general tuning)
   - **HRM Analysis:** Advanced mode that separates pure taps from HRM holds

---

## Quick Start

The fastest way to get started:

### 1. One-Time Setup

```bash
./setup.sh
```

This creates a virtual environment and installs dependencies.

### 2. Run the Automated Workflow

```bash
./quick-start.sh
```

This script:
1. Cleans old logs
2. Starts the keyboard logger
3. Displays the typing test script
4. Waits for you to type
5. Analyzes your data
6. Shows recommendations

### 3. Type Through the Test Script

Open a text editor and type through the displayed script. The script includes:
- Normal words with HRM keys (f, j)
- Intentional capital letters using HRM holds
- Space + key combinations for quotes
- Fast "flow state" typing to reveal timing issues

Press **Control-C** when finished.

### 4. Review Recommendations

The analysis will show:
- Current vs recommended timing values
- Statistical breakdown of your typing
- Specific ZMK configuration snippets to copy

---

## Detailed Setup

### Requirements

- **Operating System:** macOS (tested), Linux (should work), Windows (may need adjustments)
- **Python:** 3.8 or newer
- **Keyboard:** Any ZMK-based keyboard (Glove80, Piantor, Corne, etc.)
- **Permissions:** Accessibility/Input Monitoring access (macOS will prompt)

### Manual Installation

If you prefer manual setup over `./setup.sh`:

1. **Clone the repository:**

```bash
git clone https://github.com/dsifry/hrm-tuner.git
cd hrm-tuner
```

2. **Create virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Granting Permissions (macOS)

When you first run the logger, macOS will ask for **Input Monitoring** permissions:

1. Go to **System Preferences** → **Privacy & Security** → **Input Monitoring**
2. Enable access for **Terminal** or **iTerm** (whichever you're using)
3. Restart your terminal

---

## Usage Workflows

### Workflow A: Quick Start (Automated)

**Best for:** First-time users, quick analysis

```bash
./quick-start.sh
```

Follow the on-screen instructions.

---

### Workflow B: Manual Step-by-Step

**Best for:** Advanced users, custom testing

#### Step 1: Start the Logger

```bash
source venv/bin/activate
python3 main.py start
```

The logger runs in the background, saving data to `./log/` every 30 seconds.

#### Step 2: View the Test Script

```bash
cat TYPING-SCRIPT-HRM
```

This shows 12 sections testing different HRM patterns.

#### Step 3: Type the Test

Open a text editor (not your terminal!) and type through the script. Focus on:
- Typing naturally at your normal speed
- Don't worry about typos (we only care about timing!)
- Complete all 12 sections for comprehensive data

#### Step 4: Stop the Logger

Press **Control-C** in the terminal running the logger.

#### Step 5: Run Analysis

**Option A: HRM-Specific Analysis (Recommended)**

```bash
python3 hrmAnalysis.py
```

This separates pure taps from HRM holds for accurate recommendations.

**Option B: Simple Analysis**

```bash
python3 simpleAnanlysis.py --verbose
```

Available flags:
- `--aggressive`: Suggests lower timing values (snappier, more risk)
- `--zmk`: Outputs ZMK behavior binding format
- `--verbose`: Includes detailed comments
- `--no-explanation`: Suppresses explanatory text

---

### Workflow C: Custom Testing

**Best for:** Testing specific timing changes

1. Make changes to your ZMK keymap
2. Flash to keyboard
3. Start logger: `python3 main.py start`
4. Type naturally for 5-10 minutes
5. Stop logger (Control-C)
6. Run analysis: `python3 hrmAnalysis.py`
7. Compare before/after results

---

## Understanding the Analysis

### HRM Analysis Output (`hrmAnalysis.py`)

The advanced analysis shows:

#### 1. Pure Tap Statistics

```
Key 'f' Pure Taps (n=127):
  Average: 28.3ms
  Std Dev: 12.1ms
  Min: 8.2ms
  Max: 67.4ms
  95th percentile: 48.9ms
```

**What this means:**
- When you tap 'f' normally (not using it as Shift), you release it within 48.9ms 95% of the time
- Your `tapping-term-ms` should be higher than this (e.g., 150ms gives safe margin)

#### 2. HRM Hold Statistics

```
Key 'j' as Shift (n=45):
  Activation time (press 'j' → press next key):
  Average: 89.2ms
  Min: 52.3ms
  5th percentile: 58.7ms
```

**What this means:**
- When intentionally using 'j' as Shift, you typically press the next key 89ms later
- Your `tapping-term-ms` of 150ms works (gives you 60ms+ buffer)

#### 3. Overlap Warnings

```
⚠️  WARNING: Overlapping distributions detected for 'f'
  Max tap: 67.4ms
  Min hold activation: 52.3ms
  Recommendation: Use 'balanced' flavor or increase tapping-term-ms
```

**What this means:**
- Sometimes your fast taps overlap with slow holds (problematic!)
- Solution: Switch from "tap-preferred" to "balanced" flavor

#### 4. ZMK Recommendations

```
Recommended ZMK Configuration:

INDEX_HOLDING_TIME = 150ms  // tapping-term-ms for f/j
INDEX_HOLDING_TYPE = "balanced"  // Flavor
INDEX_STREAK_DECAY = 50ms  // require-prior-idle-ms

SPACE_HOLDING_TIME = 200ms  // For space layer access
```

---

### Simple Analysis Output (`simpleAnanlysis.py`)

Shows basic statistics for all keys:

```
Key Statistics:
'f': avg=45.2ms, std=15.3ms, min=12.1ms, max=127.8ms
'j': avg=38.7ms, std=18.2ms, min=9.4ms, max=156.3ms
'SPACE': avg=2.6ms, std=8.1ms, min=0.8ms, max=105.2ms
```

**Good for:** Quick overview, general tuning

---

## Applying Recommendations to ZMK

### Understanding ZMK Timing Parameters

Your ZMK keymap defines HRM behavior with these parameters:

#### 1. `tapping-term-ms` (Tap/Hold Threshold)

**What it does:** Time threshold separating taps from holds

```c
&mt LSHIFT F  // hold-tap: Left Shift when held, 'f' when tapped
tapping-term-ms = <150>;  // 150ms threshold
```

- **Too low (e.g., 100ms):** Normal typing triggers modifiers
- **Too high (e.g., 300ms):** Intentional holds feel sluggish
- **Recommendation:** Use your 95th percentile tap time + 50-100ms margin

#### 2. `quick-tap-ms` (Key Repeat Threshold)

**What it does:** Allows repeating keys without triggering hold

```c
quick-tap-ms = <200>;
```

**Example:** Typing "ffff" quickly
- Without `quick-tap-ms`: Might trigger shift after first 'f'
- With `quick-tap-ms = 200`: Treats rapid repeats as taps

#### 3. `require-prior-idle-ms` (Anti-Roll Protection)

**What it does:** Prevents activation during fast rolling/sliding

```c
require-prior-idle-ms = <50>;
```

**Example:** Typing "just" quickly with finger roll
- Without `require-prior-idle-ms`: 'j' might activate as Shift → "Just"
- With `require-prior-idle-ms = 50`: 'j' stays as letter if previous key was <50ms ago

#### 4. `flavor` (Decision Algorithm)

**Options:**
- **`tap-preferred`:** Waits for key release to decide (laggy)
- **`balanced`:** Decides on next keypress (recommended!)
- **`hold-preferred`:** Activates hold quickly (aggressive)

```c
flavor = "balanced";
```

### Example ZMK Configuration

Based on analysis results, your keymap might look like:

```c
// Timing constants (top of keymap)
#define TAPPING_RESOLUTION 200
#define INDEX_HOLDING_TIME 150      // f/j keys
#define INDEX_HOLDING_TYPE "balanced"
#define INDEX_STREAK_DECAY 50       // require-prior-idle-ms
#define SPACE_HOLDING_TIME 200      // space bar

// Behavior definitions
/ {
    behaviors {
        // Right Index HRM (j key)
        RightIndex: right_index_hrm {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            flavor = INDEX_HOLDING_TYPE;
            tapping-term-ms = <INDEX_HOLDING_TIME>;
            quick-tap-ms = <TAPPING_RESOLUTION>;
            require-prior-idle-ms = <INDEX_STREAK_DECAY>;
            bindings = <&kp>, <&kp>;
            hold-trigger-key-positions = <LEFT_HAND_KEYS>;
        };
    };
};
```

---

## Project Structure

### Key Files

| File | Purpose |
|------|---------|
| `setup.sh` | One-time setup script (creates venv, installs deps) |
| `quick-start.sh` | Automated workflow (start logger → analyze → report) |
| `main.py` | Starts/stops keyboard logger |
| `hrmAnalysis.py` | **Advanced HRM analysis** (separates taps from holds) |
| `simpleAnanlysis.py` | Basic per-key statistics |
| `TYPING-SCRIPT-HRM` | Comprehensive 12-part test script for HRMs |
| `TYPING-SCRIPT` | Original generic typing test |
| `requirements.txt` | Python dependencies |

### Supporting Files

| File | Purpose |
|------|---------|
| `keyboard_logger.py` | Core logging logic (pynput-based) |
| `input_logger.py` | Base class for loggers |
| `constants.py` | Configuration constants |
| `log.py` | Log file I/O |
| `utils.py` | Helper functions |

### Generated Files

| Path | Contents |
|------|----------|
| `log/*.json` | Raw keystroke logs (timestamped) |
| `venv/` | Python virtual environment |

---

## Troubleshooting

### "This process is not trusted! Input event monitoring will not be possible"

**Cause:** macOS hasn't granted Input Monitoring permissions

**Fix:**
1. Open **System Preferences** → **Privacy & Security** → **Input Monitoring**
2. Click the lock icon and authenticate
3. Enable checkbox for **Terminal** (or iTerm, etc.)
4. **Fully quit and restart** your terminal app
5. Run the logger again

### "python: command not found"

**Cause:** Need to use `python3` on macOS/Linux

**Fix:** Always use `python3` instead of `python`:
```bash
python3 main.py start
python3 hrmAnalysis.py
```

Or activate the virtual environment first:
```bash
source venv/bin/activate
python main.py start  # Now 'python' works
```

### Logger Exits Immediately

**Possible causes:**
1. Permissions not granted (see above)
2. Not running in background properly

**Fix:** Use `main.py` instead of calling `keyboard_logger.py` directly:
```bash
python3 main.py start  # Correct
```

### Analysis Shows "No data for key X"

**Cause:** You didn't type enough samples of that key

**Fix:** Type more of that key naturally. The test script includes specific sections for each HRM key.

### "KeyError: 'j'" in hrmAnalysis.py

**Cause:** No HRM hold data captured for that key

**Impact:** Minor - the script still outputs useful data before crashing

**Workaround:** Use simpleAnanlysis.py for basic stats, or ensure you type intentional capitals using the HRM in the test.

---

## Advanced Topics

### Different HRM Flavors Explained

#### tap-preferred (Laggy but Safe)
- **Behavior:** Waits for key release before deciding
- **Pros:** Very safe, rarely misfires
- **Cons:** Feels laggy, delays output
- **Use case:** Very fast typists who need maximum safety

#### balanced (Recommended)
- **Behavior:** Decides when next key is pressed
- **Pros:** Responsive, minimal lag, works for most
- **Cons:** Requires good timing tuning
- **Use case:** Most users (default recommendation)

#### hold-preferred (Aggressive)
- **Behavior:** Activates hold quickly if held past threshold
- **Pros:** Very snappy modifier activation
- **Cons:** More prone to misfires during fast typing
- **Use case:** Deliberate typers, gaming

### Bilateral vs. Positional Hold-Tap

**Bilateral Hold-Tap:**
- Only activates modifier when used with opposite hand
- Example: 'f' as Shift only works with right-hand keys

```c
hold-trigger-key-positions = <RIGHT_HAND_KEYS>;
```

**Why use it:**
- Prevents "jjjj" from triggering shift
- Safer for same-hand rolls

### Testing Workflow for Timing Changes

1. **Establish Baseline:** Run initial analysis, note current misfire rate
2. **Make Small Changes:** Adjust one parameter at a time (±20ms)
3. **Test Extensively:** Type naturally for 30+ minutes
4. **Re-analyze:** Run hrmAnalysis.py, compare statistics
5. **Iterate:** Fine-tune based on results

### Understanding 95th Percentile

**Why not use max/min?**
- Outliers (accidental long presses, hardware glitches) skew data
- 95th percentile = "95% of your typing is faster than this"
- Provides safe threshold while ignoring outliers

**Example:**
```
Tap times: [20ms, 22ms, 25ms, 28ms, 30ms, ..., 150ms (outlier)]
Max: 150ms (misleading!)
95th percentile: 48ms (realistic)
```

---

## Real-World Example

### Before Tuning

**Keymap Settings:**
```c
INDEX_HOLDING_TIME = 220ms
INDEX_HOLDING_TYPE = "tap-preferred"
SPACE_HOLDING_TIME = 220ms
```

**Problems:**
- Typing "jgood" → "jgood" (not "Good" - modifier didn't activate)
- Space+I accidentally triggers cursor up
- Feels laggy waiting for key release

### After Analysis

**Your Data:**
```
'j' pure taps: avg 23.5ms, 95th percentile 45ms
'j' as Shift activation: avg 89ms, min 52ms
'space' taps: avg 2.6ms, max 90.4ms
```

**New Settings:**
```c
INDEX_HOLDING_TIME = 150ms  // Well above 45ms tap threshold
INDEX_HOLDING_TYPE = "balanced"  // Decides on next keypress
INDEX_STREAK_DECAY = 50ms  // Prevents rolls
SPACE_HOLDING_TIME = 200ms  // Above 90ms max tap
```

**Results:**
- "jgood" → "Good" ✓ (modifier activates reliably)
- Space+I → "i" (not cursor movement) ✓
- Feels snappy and responsive ✓

---

## Contributing

Found a bug? Have a feature request?

1. Open an issue at: https://github.com/dsifry/hrm-tuner/issues
2. Include your OS, Python version, and keyboard model
3. Attach relevant log files or analysis output

Pull requests welcome!

---

## License

MIT License - see [LICENSE.md](LICENSE.md)

**Original work:** [Chih-Yuan Huang](https://yuan64198.github.io/) (InputLogger)
**HRM analysis & modifications:** [Dave Sifry](https://github.com/dsifry)

Permission granted by original author to fork and modify under MIT License.

---

## Additional Resources

- **ZMK Documentation:** https://zmk.dev/docs/behaviors/hold-tap
- **Glove80 Layout Editor:** https://my.glove80.com
- **HRM Guide by Precondition:** https://precondition.github.io/home-row-mods
- **ZMK Discord:** https://zmk.dev/community/discord/invite

---

**Happy typing!** 🎹⌨️
