import os.path
import setuptools
from subprocess import check_output

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

# Get current __version__
# version_locals = {}
# execfile(os.path.join(LOCAL_DIR, 'mlsteam', 'version.py'), {}, version_locals)
exec(open(os.path.join(LOCAL_DIR, 'mlsteam', 'version.py')).read())

# Get sha ID
sha=0
try:
    sha=check_output("git rev-parse HEAD", shell=True)[:10]
except Exception as e:
    pass
with open(os.path.join(LOCAL_DIR, 'mlsteam', 'sha.py'), 'w') as f:
    f.write("__sha__ = '{}'\n".format(sha))

# Get requirements
requirements = []
with open(os.path.join(LOCAL_DIR, 'requirements.txt'), 'r') as infile:
    for line in infile:
        line = line.strip()
        if line and not line[0] == '#':  # ignore comments
            requirements.append(line)

setuptools.setup(
    name='mlsteam',
    version=__version__,
    description="Deep Learning GPU Training System CLI Tool",
    license='BSD',
    keywords='mlsteam',
    packages=setuptools.find_packages(),
    use_2to3=True,
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    #scripts=['bin/mc'],
    data_files=[('bin', ['bin/mc'])],
    entry_points = {
        'console_scripts':['mlsteam=mlsteam.cli:cli'],
    }
)
