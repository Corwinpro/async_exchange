import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async_exchange",
    version="0.0.1",
    author="Petr Kungurtsev",
    author_email="corwinat@gmail.com",
    description="A stock exchange simulator with python asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Corwinpro/async_exchange",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
