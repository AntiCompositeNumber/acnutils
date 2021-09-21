import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="acnutils-AntiCompositeNumber",
    version="0.0.1",
    author="AntiCompositeNumber",
    url="https://github.com/AntiCompositeNumber/acnutils",
    packages=setuptools.find_packages(),
    package_data={"acnutils": ["py.typed"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
