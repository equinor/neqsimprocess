import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neqsimprocess",
    version="0.1",
    author="Even Solbraa",
    author_email="esolbraa@gmail.com",
    description="Process models using NeqSim",
    long_description="Process models using NeqSim",
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/neqsimprocess",
    packages=['neqsimprocess'],
    package_dir={'neqsimprocess': 'neqsimprocess/'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=['neqsim', 'pydantic'],
    python_requires='>=3'
)
