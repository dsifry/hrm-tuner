#!/bin/bash

# Quick start script for HRM timing analysis

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "════════════════════════════════════════════════════════════════"
echo "  HRM Timing Analysis - Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This will help you analyze and optimize your Home Row Modifier timing"
echo "for f, j, and space keys on your Glove80."
echo ""
echo "Current settings (from your keymap):"
echo "  - TAPPING_RESOLUTION: 200ms"
echo "  - INDEX_HOLDING_TIME: 220ms (f and j)"
echo "  - SPACE_HOLDING_TIME: 220ms"
echo "  - INDEX_HOLDING_TYPE: tap-preferred"
echo ""
echo "────────────────────────────────────────────────────────────────"
echo ""

# Check if log directory exists
if [ ! -d "./log" ]; then
    echo "Creating log directory..."
    mkdir -p log
fi

# Check if there are existing logs
LOG_COUNT=$(ls -1 ./log/keyboard_log_*.json 2>/dev/null | wc -l)
if [ $LOG_COUNT -gt 0 ]; then
    echo "⚠️  Found $LOG_COUNT existing log file(s)."
    echo ""
    read -p "Do you want to (C)lear old logs and start fresh, or (K)eep them? [C/k]: " answer
    answer=${answer:-C}
    if [[ $answer =~ ^[Cc]$ ]]; then
        echo "Clearing old logs..."
        python3 main.py clean
        echo "✓ Logs cleared"
    else
        echo "✓ Keeping existing logs (will analyze all of them)"
    fi
    echo ""
fi

echo "────────────────────────────────────────────────────────────────"
echo "Step 1: Type the test script"
echo "────────────────────────────────────────────────────────────────"
echo ""
echo "The keyboard logger is about to start."
echo "When it does:"
echo ""
echo "  1. Open TYPING-SCRIPT-HRM in another window/editor"
echo "  2. Type through all 11 sections NATURALLY at YOUR speed"
echo "  3. ⚠️  TYPOS ARE OK! We only measure timing, not accuracy!"
echo "  4. Type in flow state - errors are expected and ignored"
echo "  5. Press Control-C when you finish Part 11"
echo ""
echo "To view the test script, run this in another terminal:"
echo "  cat TYPING-SCRIPT-HRM"
echo ""
echo "Or open it in your editor:"
echo "  open TYPING-SCRIPT-HRM"
echo ""
read -p "Ready to start logging? Press Enter to begin..."
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🎯 KEYBOARD LOGGER STARTED"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  📊 Remember: We only measure TIMING, not accuracy!"
echo "  ✅ Type fast and naturally"
echo "  ✅ Typos and errors are HELPFUL data"
echo "  ✅ Don't slow down or fix mistakes"
echo "  ⭐ Part 11 (flow state) is the most important!"
echo ""
echo "  Press Control-C when done."
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Start the logger
python3 main.py start

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✓ LOGGING COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "────────────────────────────────────────────────────────────────"
echo "Step 2: Analyze your typing data"
echo "────────────────────────────────────────────────────────────────"
echo ""
read -p "Ready to analyze? Press Enter to continue..."
echo ""

# Run the HRM analysis
python3 hrmAnalysis.py --verbose

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✓ ANALYSIS COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "  1. Review the ZMK config recommendations above"
echo "  2. Copy the suggested values to your keymap file"
echo "  3. Flash your Glove80 with the updated config"
echo "  4. Test in real usage"
echo "  5. Run this script again if you need to fine-tune"
echo ""
echo "For more details, see: ANALYSIS-PLAN.md"
echo ""
echo "Happy typing! 🎹"
echo ""
