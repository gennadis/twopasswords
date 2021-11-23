from setuptools import setup, find_packages


with open("README.md", "r") as readme:
    long_description = readme.read()


setup(
    name="twopasswords",
    version="0.0.14",
    description="Password manager with face recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gennadis/twopasswords",
    author="Gennady Badinov",
    author_email="gennady.badinov@gmail.com",
    license="MIT",
    include_package_data=True,
    # package_dir={"twopasswords": "src"},
    packages=find_packages(),
    # packages=[
    #     "twopasswords",
    #     "twopasswords.config",
    #     "twopasswords.utils",
    #     "twopasswords.views",
    # ],
    install_requires=[
        "cmake",
        "py-cui",
        "opencv-python",
        "face-recognition",
        "sqlcipher3==0.4.5",
        "pyperclip",
        "PyYAML",
        "Faker",
    ],
    entry_points={
        "console_scripts": [
            "twopasswords = twopasswords.twopasswords:main",
        ],
    },
    classifiers=[
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
    ],
)
