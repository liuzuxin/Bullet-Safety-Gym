import sys
from setuptools import setup, find_packages


assert sys.version_info.major == 3 and sys.version_info.minor >= 6, \
    "Bullet-Safety-Gym uses Python 3.6 and above. "

with open('README.md', 'r') as f:
    # description from readme file
    long_description = f.read()

setup(
    name='bullet_safety_gym',
    version='1.1.0',
    author='Sven Gronauer',
    author_email='sven.gronauer@tum.de',
    description='A framework to benchmark safety in Reinforcement Learning.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'bullet_safety_gym.envs': ['data/**/*'],
    },
    license='MIT license',
    url='https://github.com/liuzuxin/Bullet-Safety-Gym',
    install_requires=['gym>=0.26.0', 'numpy>1.16.0', 'pybullet>=3.0.6'],
    python_requires='>=3.6',
    platforms=['Linux Ubuntu', 'darwin'],  # supports Linux and Mac OSX
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
