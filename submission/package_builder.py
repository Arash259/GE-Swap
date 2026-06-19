"""
package_builder.py - Zips all necessary files for journal submission.
"""

import os
import zipfile
import shutil

def build_package(output_zip='submission_package.zip'):
    temp = 'temp_submission'
    os.makedirs(temp, exist_ok=True)
    for d in ['core', 'analysis', 'experiments', 'output', 'utils']:
        if os.path.exists(d):
            shutil.copytree(d, os.path.join(temp, d), dirs_exist_ok=True)
    shutil.copy('main.py', temp)
    shutil.copy('config.py', temp)
    shutil.copy('requirements.txt', temp)
    with zipfile.ZipFile(output_zip, 'w') as zf:
        for root, _, files in os.walk(temp):
            for f in files:
                zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), temp))
    shutil.rmtree(temp)
    print(f"Package built: {output_zip}")