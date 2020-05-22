# Typeshift solver
A solver for the mobile game ![Typeshift](https://play.google.com/store/apps/details?id=com.noodlecake.typeshift&hl=en_US) using OpenCV, Tesseract and ADB

## Requirements

You need to have Android Debugging Bridge installed along with any relevant drivers for your phone. You also need
to have Python installed along with the packages:

* opencv
* pytesseract
* imutils
* kanren (entirely optional if you want to use the other __slow__ solver)

## Running

1. Ensure that your android phone is connected and that USB debugging is enabled. 
1. Run `adb devices` to start the daemon and ensure your device is listed.
1. Start typeshift on your phone and open up a puzzle.
1. Run `python solve.py` and watch the magic happen.

## Caveats

* Sometimes tesseract does not identify the character correctly e.g indetifying '0' instead of 'O' which messes with the whole
  process
* The solver relies on you supplying a sufficiently large word list in my case I was able to use the one at `/usr/share/dict/words` which comes from installing the `words` package on Arch Linux. The file can be found ![here](https://ftp.gnu.org/gnu/aspell/dict/0index.html)
* The solver is only for the puzzles that involve alinging characters in a column to form a word.
* Instead of entering a certain amount of words it should instead keep entering
  words until the puzzle is solved.
