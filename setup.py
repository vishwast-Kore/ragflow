import os
from setuptools import find_packages, setup
from pathlib import Path
PACKAGE_NAME = "ragflow"
# Reading the packages from requirements.txt
with open('./ragflow/requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    description="Efficient Document-Based QA with Retrieval-Augmented Generation (RAG) and Large Language Models (LLM).",
    long_description="",
    long_description_content_type="text/markdown",
    author='vishwast-Kore',
    author_email='vishwas.tak@kore.com',
    license='Apache 2.0',
    platforms=["Mac", "Linux", "Windows"],
    packages=['ragflow'],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Scientific/Engineering',  # 科学和工程主题
    'Topic :: Scientific/Engineering :: Artificial Intelligence',  # 人工智能主题
    'Topic :: Software Development :: Libraries :: Python Modules',  # Python模块库
    ]
)