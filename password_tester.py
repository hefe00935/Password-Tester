import customtkinter as ctk
import tkinter.font as tkfont
from tkinter import TclError, messagebox, IntVar, BooleanVar
import itertools
import string
import time
import threading
import os

# Optional font file next to the script
font_path = os.path.join(os.path.dirname(__file__), "Fredoka", "Fredoka-VariableFont_wdth,wght.ttf")

app = ctk.CTk()
app.title("🔐 Brute-Force Password Tool")
app.geometry("700x640")
app.resizable(False, False)

# Font fallback (optional)
try:
    tkfont.nametofont("Fredoka")
except TclError:
    app.tk.call("font", "create", "Fredoka", "-family", font_path)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_fredoka_font(size=18):
    return ("Fredoka", size)

# stop event for clean cancellation
stop_event = threading.Event()

# --- GUI ---
label_title = ctk.CTkLabel(app, text="🔐 Brute-Force Password Tool", font=get_fredoka_font(28))
label_title.pack(pady=12)

label_desc = ctk.CTkLabel(
    app,
    text="Enter up to 3 target passwords. Configure character set and max length, then click Start.\nThe search will stop when all targets are found (or when you press Stop).",
    font=get_fredoka_font(13),
    wraplength=660
)
label_desc.pack(pady=(0, 8))

entries_frame = ctk.CTkFrame(app)
entries_frame.pack(pady=6)

entries = []
for i in range(3):
    entry = ctk.CTkEntry(entries_frame, placeholder_text=f"Password {i+1}", font=get_fredoka_font(14), width=430)
    entry.grid(row=i, column=0, pady=6, padx=6)
    entries.append(entry)

options_frame = ctk.CTkFrame(app)
options_frame.pack(pady=8, fill="x", padx=12)

# Max length using IntVar (safe)
maxlen_label = ctk.CTkLabel(options_frame, text="Max length:", font=get_fredoka_font(14))
maxlen_label.grid(row=0, column=0, padx=(12,6), pady=8, sticky="w")
maxlen_var = IntVar(value=4)
maxlen_entry = ctk.CTkEntry(options_frame, textvariable=maxlen_var, width=90, font=get_fredoka_font(14))
maxlen_entry.grid(row=0, column=1, padx=(0,12), pady=8, sticky="w")

# Charset options
charset_label = ctk.CTkLabel(options_frame, text="Characters to include:", font=get_fredoka_font(14))
charset_label.grid(row=1, column=0, padx=(12,6), pady=6, sticky="w")

lower_var = BooleanVar(value=True)
upper_var = BooleanVar(value=False)
digits_var = BooleanVar(value=True)
symbols_var = BooleanVar(value=False)

lower_cb = ctk.CTkCheckBox(options_frame, text="lowercase", variable=lower_var, font=get_fredoka_font(12))
lower_cb.grid(row=1, column=1, sticky="w", padx=(0,8))
upper_cb = ctk.CTkCheckBox(options_frame, text="UPPERCASE", variable=upper_var, font=get_fredoka_font(12))
upper_cb.grid(row=1, column=2, sticky="w", padx=(0,8))
digits_cb = ctk.CTkCheckBox(options_frame, text="digits", variable=digits_var, font=get_fredoka_font(12))
digits_cb.grid(row=1, column=3, sticky="w", padx=(0,8))
symbols_cb = ctk.CTkCheckBox(options_frame, text="symbols", variable=symbols_var, font=get_fredoka_font(12))
symbols_cb.grid(row=1, column=4, sticky="w", padx=(0,8))

controls_frame = ctk.CTkFrame(app)
controls_frame.pack(pady=(6, 12))

start_button = ctk.CTkButton(controls_frame, text="Start", font=get_fredoka_font(16))
start_button.grid(row=0, column=0, padx=8)

stop_button = ctk.CTkButton(controls_frame, text="Stop", font=get_fredoka_font(16), fg_color="#b22222")
stop_button.grid(row=0, column=1, padx=8)
stop_button.configure(state="disabled")

# Log textbox
textbox = ctk.CTkTextbox(app, width=660, height=360, font=get_fredoka_font(13))
textbox.pack(pady=8)
textbox.configure(state="disabled")

def _log(message):
    textbox.configure(state="normal")
    textbox.insert("end", message)
    textbox.see("end")
    textbox.configure(state="disabled")

def _disable_controls():
    start_button.configure(state="disabled")
    stop_button.configure(state="normal")

def _enable_controls():
    start_button.configure(state="normal")
    stop_button.configure(state="disabled")

def build_charset():
    parts = []
    if lower_var.get():
        parts.append(string.ascii_lowercase)
    if upper_var.get():
        parts.append(string.ascii_uppercase)
    if digits_var.get():
        parts.append(string.digits)
    if symbols_var.get():
        parts.append("!@#$%^&*()-_=+[]{};:,.<>/?|\\`~")
    return "".join(parts)

def brute_force_worker(passwords, max_length):
    """
    Global search: iterate all guesses once and check against remaining targets.
    Stop when all targets have been found or stop_event is set.
    """
    charset = build_charset()
    if not charset:
        _log("⚠️ No character sets selected. Aborting.\n")
        _enable_controls()
        return

    # Normalize passwords exactly as provided (case-sensitive)
    targets = list(passwords)
    remaining = set(targets)  # set of strings still to find
    results = {}  # password -> info dict when found
    total_attempts = 0
    progress_interval = 200000  # log progress every N attempts
    start_time = time.time()

    _log(f"🔎 Starting global search for {len(targets)} target(s) up to length {max_length} using {len(charset)} chars...\n")

    # Try guesses by increasing length
    for length in range(1, max_length + 1):
        if stop_event.is_set():
            break

        # product enumerates all combos of the charset repeated 'length' times
        for attempt in itertools.product(charset, repeat=length):
            if stop_event.is_set():
                break

            guess = ''.join(attempt)
            total_attempts += 1

            # periodic progress log
            if total_attempts % progress_interval == 0:
                elapsed = time.time() - start_time
                _log(f"…progress: {total_attempts} attempts, elapsed {elapsed:.1f}s (current length {length}), remaining: {len(remaining)}\n")

            # Check if this guess matches any remaining target
            if guess in remaining:
                elapsed = time.time() - start_time
                results[guess] = {
                    "password": guess,
                    "found": guess,
                    "attempts": total_attempts,
                    "time": round(elapsed, 3)
                }
                remaining.remove(guess)
                _log(f"✅ Password found: {guess} | ⏱ Time: {elapsed:.2f} s | 🔁 Attempts: {total_attempts}\n")

                # If we've found all targets, stop everything
                if not remaining:
                    stop_event.set()
                    break

        if not remaining or stop_event.is_set():
            break

    # For any targets still not found, add a not-found result (attempts/time show how far we got)
    elapsed_total = time.time() - start_time
    for pw in targets:
        if pw not in results:
            results[pw] = {
                "password": pw,
                "found": None,
                "attempts": total_attempts,
                "time": round(elapsed_total, 3)
            }
            if pw in remaining:
                _log(f"❌ Not found (up to length {max_length}): {pw}\n")

    # Summary
    _log("\n📊 Brute-force Report:\n")
    for pw in targets:
        r = results[pw]
        if r["found"]:
            _log(f"- 🔐 Password: {r['password']} | ✅ Found: {r['found']} | 🕒 Time: {r['time']} s | 🔁 Attempts: {r['attempts']}\n")
        else:
            _log(f"- 🔐 Password: {r['password']} | ❌ Not found | 🕒 Time: {r['time']} s | 🔁 Attempts: {r['attempts']}\n")

    _log(f"\nTotal attempts: {total_attempts}\n")
    _enable_controls()
    stop_event.clear()

def start_brute_force():
    # Safely read max length from IntVar; IntVar guarantees numeric type
    try:
        max_len_val = int(maxlen_var.get())
    except Exception:
        messagebox.showerror("Invalid value", "Max length must be a positive integer.")
        return

    if max_len_val < 1:
        messagebox.showerror("Invalid value", "Max length must be >= 1.")
        return

    if max_len_val > 8:
        # warn about huge search space but allow
        if not messagebox.askyesno("Warning", "Max length > 8 with many characters will be extremely slow. Continue?"):
            return

    passwords = [e.get().strip() for e in entries if e.get().strip()]
    if not passwords:
        messagebox.showwarning("No passwords", "Please enter at least one password to search for.")
        return

    # reset UI/logs/stop flag
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")
    textbox.configure(state="disabled")
    stop_event.clear()
    _disable_controls()

    threading.Thread(target=brute_force_worker, args=(passwords, max_len_val), daemon=True).start()

def stop_brute_force():
    stop_event.set()
    _log("🛑 Stop requested — finishing current iteration and exiting...\n")

start_button.configure(command=start_brute_force)
stop_button.configure(command=stop_brute_force)

app.mainloop()
