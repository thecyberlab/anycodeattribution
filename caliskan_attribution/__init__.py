import subprocess


def run_shell_script():
    subprocess.run(['./scripts/run_all_caliskan.sh'], shell=True)


run_shell_script()
