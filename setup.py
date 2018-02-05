from setuptools import setup

# https://python-packaging.readthedocs.io/en/latest/metadata.html

setup(name="tbc_adapter",
      version="0.1",
      description="TBC payment gateway adapter",
      url="https://github.com/Jambazishvili/tbc-adapter",
      author="Giorgi (mecko) Jambazishvili",
      author_email="giorgi.jambazishvili@gmail.com",
      license="MIT",
      packages=["tbc_adapter"],
      zip_safe=False,
      keywords=["TBC", "payment gateway", "online payment"],
      classifiers = [
          "Programming Language :: Python :: 3",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
      ],
      install_requires=[
          "requests",
          "pyopenssl"
      ])
