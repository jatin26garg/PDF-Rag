import psutil
import os


def measure_memory():
    """Measure system memory usage."""

    # Get total system memory
    total_memory = psutil.virtual_memory().total / (1024**3)
    used_memory = psutil.virtual_memory().used / (1024**3)
    available_memory = psutil.virtual_memory().available / (1024**3)

    # Get current Python process memory
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info().rss / (1024**3)

    # Check Ollama memory
    try:
        ollama_processes = []

        for proc in psutil.process_iter(
            ['pid', 'name', 'memory_info']
        ):
            try:
                if proc.info['name'] and 'ollama' in proc.info['name'].lower():
                    ollama_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        ollama_memory = sum(
            p['memory_info'].rss
            for p in ollama_processes
            if p['memory_info'] is not None
        ) / (1024**3)

    except Exception:
        ollama_memory = 0

    print(f"""
═══════════════════════════════════════════
              MEMORY REPORT
═══════════════════════════════════════════
Total System RAM:  {total_memory:.1f} GB
Used System RAM:   {used_memory:.1f} GB
Available RAM:     {available_memory:.1f} GB

Current Process:   {process_memory:.2f} GB
Ollama (Qwen3-8B): {ollama_memory:.2f} GB

{'✅ PASS' if available_memory > 2 else '⚠️ LOW MEMORY'}
═══════════════════════════════════════════
""")


if __name__ == "__main__":
    measure_memory()