import subprocess
import os

print(f"Current directory: {os.getcwd()}")
try:
    # Run pytest with verbose and trace-config to see what's happening
    result = subprocess.run(["python", "-m", "pytest", "tests/", "-v"], capture_output=True, text=True, encoding='utf-8')
    print("Return code:", result.returncode)
    print("STDOUT BEGIN")
    print(result.stdout)
    print("STDOUT END")
    print("STDERR BEGIN")
    print(result.stderr)
    print("STDERR END")
except Exception as e:
    print("Error running subprocess:", e)
