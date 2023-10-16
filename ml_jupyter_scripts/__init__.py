import subprocess

def run_shell_script():
    subprocess.run(['./scripts/run_ml_script.sh'], shell=True)

run_shell_script()