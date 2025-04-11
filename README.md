# HRM Tuner

A proof-of-concept typing analysis tool to help Glove80 and ZMK users tune their Home Row Modifiers (HRMs) based on their real-world typing behavior.

> This project is based on [Chih-Yuan Huang's InputLogger](https://github.com/yuan64198/InputLogger), but has been _heavily modified_ for typing analysis, modernized for current Python environments, and focused specifically on ergonomic keyboard use cases.

## What It Does

- Records high-precision keyboard input using `pynput`
- Measures actual hold times vs. tap durations on each key
- Breaks down per-key stats with mean, standard deviation, and tap/hold classification
- Generates personalized ZmKTiming thresholds (e.g. `TAPPING_RESOLUTION`, `HOMEY_HOLDING_TIME`)
- Helps eliminate HRM misfires while preserving typing speed

## Setup

### Requirements

- Python 3.8+
- Dependencies:
  - `pynput` (keyboard input)
  - `pillow` (modern version >=10.x)
- macOS (tested), should work on Linux and Windows with slight tweaks

### Installation

1. Clone the repository:

```sh
git clone https://github.com/dsifry/hrm-tuner.git
cd hrm-tuner
```

2. Create and activate a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:

```sh
pip install -r requirements.txt
```

## Usage

### 1. Record a Typing Session

1. Create the log directory:

```sh
mkdir -p log
```

2. View/prep the test script:

```sh
cat TYPING-SCRIPT
```

3. Start the keyboard logger:

```sh
python main.py start
```

The script contains a variety of typing patterns to test your HRMs, including:

- Regular typing
- Modifier combinations (⌘, ⌥, ⌃, ⇧)
- Home row mods
- Punctuation and special characters

4. When finished, press Control-C to stop the logger

### 2. Analyze Your Performance

Run the analysis script with optional arguments:

```sh
python simpleAnalysis.py [--aggressive] [--zmk]
```

Available arguments:

- `--aggressive`: Suggests lower tapping resolution values for snappier modifier activation
- `--zmk`: Outputs the configuration in ZMK-style behavior binding format for direct use in keymap files
- `--help`: Shows the help message

The analysis will show:

- Per-key hold times
- Tap vs hold buckets for HRM keys
- Average, std deviation, min, max for each key
- Suggested fields for good `config.h` based on your typing data

### Analysis Output

The analysis provides three main sections:

1. **Key Timing Analysis**

   - Shows how long you hold each key when typing
   - Includes average hold time, standard deviation, and min/max values
   - Helps identify your natural typing rhythm

2. **Home Row Modifier Analysis**

   - Focuses on home row keys (a,s,d,f,j,k,l,;)
   - Separates taps (under 200ms) from holds (over 200ms)
   - Helps tune modifier activation timing

3. **Suggested ZMK Configuration**
   - Provides difficulty level based on your typing speed
   - Suggests timing values for your ZMK config
   - Includes additional settings for fine-tuning

### Log Format

Raw keyboard logs are saved in `./log/` and structured like this (JSON):

```json
{
  "records": [
    {
      "button": "a",
      "is_on_press": true,
      "timestamp": 1712798222.123456,
      "coordinates": [0.0, 0.0]
    }
  ],
  "timestamp": "20250410_204854"
}
```

All timestamps are stored as UNIX `float` values for microsecond precision.

### Config Recommendations

The analysis script will recommend ZmKStyle `config` values (like `TAPPING_RESOLUTION`) as well as
Glorious Engrammer-style `macros` (e.g. `DETALINE_HOMEY_HOLDING_TIME`).

You can use these to customize your HRM behavior based on your actual typing data.

### Credits

- Original Project which was insipration: [Chih-Yuan Huang](https://yuan64198.github.io/)
- HRM tuning and Analysis after a significant rewrite: [Dave Sifry](https://github.com/dsifry)

### License

MIT - see `LICENSE.md` for full details.
