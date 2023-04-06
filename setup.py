import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epcis-event-hash-generator",
    keywords="epcis GS1 hashing traceability",
    version="1.8.0",
    author="""Package author: Sebastian Schmittner
    Code authors: https://github.com/RalphTro/epcis-event-hash-generator/graphs/contributors""",
    author_email="sebastian.schmittner@eecc.de",
    license="MIT",
    description="Exemplary implementation of the EPCIS event hash generator algorithm described in the README",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RalphTro/epcis-event-hash-generator",
    packages=["epcis_event_hash_generator"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "generator=epcis_event_hash_generator.main:main",
        ]
    },
    install_requires=[
        'python_dateutil>=2.8',
        'Flask>=1.1',
        'PyLD==2.0.3'
    ],
)
