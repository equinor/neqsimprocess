import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neqsim-condition-monitoring",
    version="0.1",
    author="Even Solbraa","Marlene Louisen Lund", "Knut Maråk"
    author_email="esolbraa@gmail.com",
    description="Process condition monitoring using NeqSim",
    long_description="Process condition monitoring using NeqSim",
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/neqsim-condition-monitoring",
    packages=['neqsim-condition-monitoring'],
    package_dir={'neqsim-condition-monitoring': 'src/neqsim-condition-monitoring'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=['neqsim'],
    python_requires='>=3'
)
