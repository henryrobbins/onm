import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="onm",
    version="0.0.1",
    author="Henry Robbins",
    author_email="hw.robbins@gmail.com",
    description="A Python package for money management.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/henryrobbins/onm.git",
    packages=setuptools.find_packages(),
    license="MIT License",
    classifiers=[],
    install_requires=[],
    python_requires='>=3.5'
)
