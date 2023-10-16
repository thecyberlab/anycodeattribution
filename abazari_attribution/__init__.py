import subprocess


def run_shell_script():
    subprocess.run(['./scripts/run_all_abazari.sh'], shell=True)


run_shell_script()
