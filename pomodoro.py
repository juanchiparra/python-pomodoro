import time
import os
import sys
import shutil
import datetime
import math

# Default time values (in seconds)
POMODORO = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60

# Bell mode: 'auto', 'tone', 'ascii', or 'off'
# 'tone' (Windows) or 'ascii' (others) by default
BELL_MODE = 'tone' if os.name == 'nt' else 'ascii'

# Default ANSI colors
RESET = "\x1b[0m" # reset all attributes
GREEN = "\x1b[92m" # bright green
YELLOW = "\x1b[93m" # bright yellow
RED = "\x1b[91m" # bright red
GREY = "\x1b[90m" # Grey
USE_COLOR = sys.stdout.isatty() # True if stdout is an interactive TTY; enable ANSI colors only for terminals

# Clear the terminal screen
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Render the status/progress line in the terminal
def render_status_line(total, elapsed, clock, m_rem, s_rem, bar_length=40, init=False):
    """Render a two-line status: time info and progress bar."""
    total = max(1, total)
    f = max(0.0, min(1.0, elapsed / total))
    pct = int(f * 100)
    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    info = f" Time: {clock}  |  Remaining: {m_rem}:{s_rem:02d}"
    info_line = (GREY + info + RESET) if USE_COLOR else info
    bar_len = min(bar_length, max(0, width - len(f" {pct:3d}%") - 1))
    filled = int(bar_len * f)
    if USE_COLOR:
        color = GREEN if f < 0.5 else (YELLOW if f < 0.8 else RED)
        bar = color + '█' * filled + RESET
        if bar_len > filled:
            bar += GREY + '░' * (bar_len - filled) + RESET
    else:
        bar = '#' * filled + '-' * (bar_len - filled)

    if init:
        sys.stdout.write("\r\x1b[2K" + info_line + "\n")
        sys.stdout.write("\r\x1b[2K" + bar + f" {pct:3d}%")
    else:
        sys.stdout.write("\x1b[1A")
        sys.stdout.write("\r\x1b[2K" + info_line + "\n")
        sys.stdout.write("\r\x1b[2K" + bar + f" {pct:3d}%")
    sys.stdout.flush()

# Sound mode: 'off' silent | 'tone' (Windows beep(freq,ms)) | 'ascii'/'auto' -> terminal bell '\a'
def beep(freq=1000, ms=250):
    """Emit a bell.
    BELL_MODE: 'off' silent; 'tone' -> winsound.Beep on Windows; 'ascii'/'auto' -> write '\a'.
    """
    mode = globals().get('BELL_MODE', 'auto')
    if mode == 'off':
        return
    
    # Prefer tonal beep on Windows when requested
    if os.name == 'nt' and mode in ('auto', 'tone'):
        try:
            import winsound
            winsound.Beep(int(freq), int(ms))
            return
        except Exception:
            pass

    # Fallback to ASCII bell
    if mode in ('auto', 'ascii', 'tone'):
        try:
            sys.stdout.write('\a')
            sys.stdout.flush()
        except Exception:
            pass

# Beep multiple times with a short gap
def beep_n(times=2, freq=1000, ms=200, gap=0.05):
    """Beep multiple times with a short gap."""
    for _ in range(max(0, times)):
        beep(freq=freq, ms=ms)
        time.sleep(max(0.0, gap))

# Run a single timer with a live progress bar and final beeps
def pomodoro_timer(duration, message, *, beep_times=2, beep_freq=1000, beep_ms=250, beep_gap=0.07):
    """Run a single timer with a live progress bar and final beeps."""
    clear_screen()
    print(f"--- {message} ---")
    start = time.monotonic()
    end = start + duration

    try:
        first = True
        while True:
            now = time.monotonic()
            if now >= end:
                break
            rem = max(0.0, end - now)
            elapsed = duration - rem
            clock = datetime.datetime.now().strftime('%I:%M %p')
            render_status_line(duration, elapsed, clock, int(rem // 60), int(rem % 60), init=first)
            first = False
            next_tick = start + math.floor(elapsed) + 1
            time.sleep(max(0.0, min(1.0, next_tick - time.monotonic())))
    except KeyboardInterrupt:
        print('\nInterrupted by user.')
        return

    print('\nTime is up!')
    beep_n(times=beep_times, freq=beep_freq, ms=beep_ms, gap=beep_gap)

def main():
    pomodoro, short, long_break = POMODORO, SHORT_BREAK, LONG_BREAK
    cycles = 0
    while True:
        pomodoro_timer(pomodoro, 'WORK', beep_times=1, beep_freq=800, beep_ms=400, beep_gap=0.08)
        cycles += 1
        if cycles % 4 == 0:
            pomodoro_timer(long_break, 'LONG BREAK', beep_times=1, beep_freq=950, beep_ms=200, beep_gap=0.07)
        else:
            pomodoro_timer(short, 'SHORT BREAK', beep_times=1, beep_freq=900, beep_ms=170, beep_gap=0.06)
            prompt = (GREY + 'Press enter to continue...' + RESET) if USE_COLOR else 'Press enter to continue...'
            input(prompt)

if __name__ == '__main__':
    main()