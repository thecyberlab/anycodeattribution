import subprocess

def run_shell_script():
    subprocess.run(['./scripts/run_all_zaffar.sh'], shell=True)

run_shell_script()