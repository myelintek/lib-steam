import os.path
import setuptools
from subprocess import check_output

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

# Get current __version__
version_locals = {}
execfile(os.path.join(LOCAL_DIR, 'mlsteam', 'version.py'), {}, version_locals)

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
    version=version_locals['__version__'],
    description="Deep Learning GPU Training System CLI Tool",
    license='BSD',
    classifiers=[
        'Framework :: Flask',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='mlsteam',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    scripts=['bin/mc'],
    entry_points = {
        'console_scripts':['mlsteam=mlsteam.cli:cli'],
    }
)
