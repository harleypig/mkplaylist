
from setuptools import setup, find_packages
import os

# Read the long description from README.md if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
  name="mkplaylist",
  version="0.1.0",
  description="Create Spotify playlists based on custom criteria using Last.fm data",
  long_description=long_description,
  long_description_content_type="text/markdown",
  author="harleypig",
  author_email="harleypig@gmail.com",
  url="https://github.com/harleypig/mkplaylist",
  project_urls={
      "Bug Tracker": "https://github.com/harleypig/mkplaylist/issues",
      "Documentation": "https://github.com/harleypig/mkplaylist/tree/main/docs",
      "Source Code": "https://github.com/harleypig/mkplaylist",
  },

  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    "spotipy>=2.19.0",
    "pylast>=5.0.0",
    "sqlalchemy>=1.4.0",
    "click>=8.0.0",
    "python-dotenv>=0.19.0",
  ],
  extras_require={
    "dev": [
      "pytest>=6.0.0",
      "pytest-cov>=2.12.0",
      "black>=21.5b2",
      "isort>=5.9.0",
      "flake8>=3.9.0",
      "pre-commit>=2.13.0",
    ],
  },
  entry_points={
    "console_scripts": ["mkplaylist=mkplaylist.cli:main", ],
  },
  python_requires=">=3.7",
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Multimedia :: Sound/Audio",
  ],
)
