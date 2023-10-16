import subprocess


def run_shell_script():
    subprocess.run(['./scripts/run_all_ding.sh'], shell=True)


run_shell_script()
