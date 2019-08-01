import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tesdaq",
    version="0.0.5",
    author="Connor Duncan",
    author_email="ctdunc@berkeley.edu",
    description="DAQ Control using Redis as a message broker.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ucbpylegroup/tesdaq",
    packages=['tesdaq', 'tesdaq.listen', 'tesdaq.command', 'tesdaq.daq_constants'],
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research"
    ],
    install_requires=[
        "numpy==1.16.4",
        "redis==3.2.1",
        ]
)
