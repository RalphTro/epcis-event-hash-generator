import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epcis-event-hash-generator",
    version="1.0.1",
    author=" Ralph Troeger; Sebastian Schmittner",
    author_email="ralph.troeger@gs1.de;schmittner@eecc.info",
    description="Exemplary implementation of the epcis event hash generator algorithm described in the README",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RalphTro/epcis-event-hash-generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)