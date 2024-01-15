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
    include_package_data=True,
    package_data={'onm': ['data/*', 'html/*']},
    license="MIT License",
    classifiers=[],
    entry_points={
        'console_scripts': [
            'onm = onm.main:cli',
        ],
    },
    install_requires=[],
    python_requires='>=3.5'
)
