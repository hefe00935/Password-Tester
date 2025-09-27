# 🔐 Brute-Force Password Tool

**A small educational GUI tool (CustomTkinter) that demonstrates a global brute-force search across up to 3 target passwords.**

> **Important:** This project is for *education, testing, and defensive/security research only.* Do **not** use it to access, damage, or attempt to compromise accounts, systems, or data you do not own or have explicit permission to test. Misuse may be illegal and unethical.
---

## About

This repository contains a compact Python application that enumerates candidate passwords using a configurable character set and length, and checks those guesses against up to **three** user-specified target strings.

The program is implemented with `customtkinter` for a modern UI and uses `itertools.product` to iterate guesses. The search stops automatically when all provided targets have been found (or when you press **Stop**).

This is intended for learning how brute-force enumeration behaves and to demonstrate performance/UX trade-offs for very large search spaces.

---

## Features

* Enter up to **3** target passwords to search for.
* Toggle which character groups to include: lowercase, UPPERCASE, digits, symbols.
* Configure maximum password length (1..N).
* Global search strategy: enumerates each candidate once and checks against all remaining targets.
* Live progress log and summary report when complete.
* Start / Stop buttons and clean cancellation using a thread-safe event.

---

## Requirements

* Python **3.8+** (3.10/3.11 recommended)
* `customtkinter` (modern Tkinter wrapper)

Optional:

* A local copy of the optional Fredoka variable font placed next to the script in `./Fredoka/Fredoka-VariableFont_wdth,wght.ttf` (the app will fall back to a system font if not present).

---

## Installation

1. Clone this repository:

```bash
git clone <repo-url>
cd <repo-folder>
```
  

3. Install the dependency:

```bash
pip install customtkinter
```

> If `customtkinter` is not available via pip for your environment, you can install the package from its source (see the CustomTkinter docs).

---

## Running

Run the script directly with Python:

```bash
python brute_force_gui.py
```

(Replace `brute_force_gui.py` with the file name you use in the repo.)

---

## GUI Controls & Explanation

* **Password 1 / Password 2 / Password 3**: enter the exact strings you want the tool to search for. The search is case-sensitive.
* **Max length**: maximum length to enumerate (searches from length 1 to this value). Enter an integer value.
* **Character toggles**: choose which sets of characters to include in guesses (lowercase, UPPERCASE, digits, symbols).
* **Start / Stop**: Start begins the search in a background thread; Stop requests graceful cancellation (finishes the current iteration and stops).
* **Log**: a running text log shows progress messages, found passwords, and a final summary.

**Important usability note:** brute-force search grows exponentially with length and character set size. Keep `max length` small during testing.

---

## Implementation notes & performance

* Enumeration uses `itertools.product(charset, repeat=length)` and checks guessed strings against a `set` of remaining targets for O(1) membership tests.
* The GUI runs the worker in a Python `threading.Thread` and uses a `threading.Event` for stop requests.
* **CPU vs GPU:** This implementation is CPU-bound — there is no GPU acceleration. Python loops and `itertools` run on the CPU. If you need to speed up enumeration, consider:

  * Using the `multiprocessing` module to distribute work across processes (bypass the GIL for CPU-bound workloads).
  * Implementing the core generator in a compiled language (C/C++, Rust) or using specialized GPU libraries — but that is advanced and outside this repo's scope.
* `threading` here is used to keep the GUI responsive; due to the GIL, heavy CPU work will still be limited in pure-Python threads. Use `multiprocessing` for parallel speedups.

---

## Security & Ethics

This project demonstrates how simple brute-force enumeration works. **Do not** use it to try to access any systems, accounts, or services without explicit written permission from the owner. Unauthorized access is illegal in many jurisdictions.

If your intention is defensive/security testing, always obtain written authorization (a signed scope/staging test agreement) before running any attack simulation.

---

## Suggested improvements

If you'd like to extend this project, here are recommended improvements:

* Add `multiprocessing` worker pool to distribute candidate ranges across CPU cores.
* Add checkpointing and resume capability for very long runs.
* Add an exportable report (CSV/JSON) and optional log level toggles.
* Add rate-limiting / pause between attempts for faster GUI responsiveness.
* Add a performance estimator that computes an approximate search space size and expected time at a given attempts/sec.
* Add unit tests and a CI workflow.

---

## Contributing

Contributions are welcome if they keep the repo focused on education and ethical research. Please open an issue to discuss larger changes before submitting a PR.

Suggested workflow:

1. Fork the repo
2. Create a feature branch
3. Add your change and tests
4. Open a pull request describing the change

---

## Troubleshooting

* **App doesn't start / `customtkinter` import error:** ensure you installed `customtkinter` into the virtual environment you launched the script from.
* **Font issues:** the Fredoka font path is optional. If the font is missing the app will use a fallback font.
* **The UI freezes or is slow:** reduce `max length`, lower the character set, or switch to a multiprocessing design.

---
