# Shared console output helpers so every stage of the patcher reports
# progress in the same clean format.

import os
import subprocess
import sys
import time

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
if _USE_COLOR and os.name == "nt":
    os.system("")  # enables ANSI escape processing in the Windows console


def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def format_time(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def banner(title):
    line = "=" * 60
    print(f"\n{_c('1;36', line)}\n{_c('1;36', '  ' + title)}\n{_c('1;36', line)}")


def step(number, total, title):
    print(f"\n{_c('1;36', f'[{number}/{total}]')} {_c('1', title)}")


def info(msg):
    print(f"  {_c('36', '-')} {msg}")


def ok(msg):
    print(f"  {_c('32', '+')} {msg}")


def warn(msg):
    print(f"  {_c('33', '!')} {_c('33', msg)}")


def error(msg):
    print(f"  {_c('31', 'x')} {_c('31', msg)}")


def progress(done, total, label=""):
    """Single-line progress bar, redrawn in place."""
    width = 30
    filled = int(width * done / total) if total else width
    bar = "#" * filled + "-" * (width - filled)
    end = "\n" if done >= total else ""
    print(f"\r  [{bar}] {done}/{total} {label}".ljust(79) + end,
          end="", flush=True)


def run(cmd, what=None):
    """Run an external tool, hiding its output unless it fails.

    Returns the exit code. A failure is reported but does not abort,
    matching the previous os.system behaviour."""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True,
                            errors="replace")
    if result.returncode != 0:
        error(f"{what or cmd} failed (exit code {result.returncode})")
        for line in result.stdout.strip().splitlines()[-15:]:
            print(f"      {line}")
    return result.returncode


def run_all(commands, label="items"):
    """Run many independent external commands in parallel with a progress bar.

    commands is a list of (cmd, what) tuples; failures are reported by run()."""
    from concurrent.futures import ThreadPoolExecutor
    workers = min(32, (os.cpu_count() or 4) * 2)
    info(f"Converting {len(commands)} {label} using {workers} workers")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run, cmd, what) for cmd, what in commands]
        for done, future in enumerate(futures, 1):
            future.result()
            progress(done, len(futures), label)


class Timer:
    def __init__(self):
        self.start = time.time()

    def elapsed(self):
        return format_time(time.time() - self.start)
