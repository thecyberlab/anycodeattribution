from setuptools import setup, find_packages

setup(
    name='Code-attribution-library',
    version='0.1',
    description='Code Attribution methods',
    author='Attribution',
    author_email='attribution@email.com',
    packages=find_packages(),
    scripts=['scripts/run_shell_script.sh', 'scripts/run_all_ding.sh', 'scripts/run_all_caliskan.sh', 'scripts/run_all_kothari.sh', 'scripts/run_all_zaffar.sh', 'scripts/run_all_abazari.sh', 'scripts/run_ml_script.sh'],  # Include your shell script here
    install_requires=[
    ]
)
