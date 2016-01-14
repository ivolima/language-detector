import os
from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

setup(
    name="languagedetector",
    version="0.1.5",
    author="Ivo Lima",
    author_email="ivo.romario@gmail.com",
    description=("Just another toolbox for Natural Language Processing"),
    long_description=README,
    license="MIT",
    keywords="nlp",
    #url="https://github.com/ivolima/languagedetector",
    url="https://bitbucket.org/ivoromario/language-detector",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['nltk'],
    #tests_require=['nose', 'coverage'],
    #test_suite='tests',
    package_data = {
        'languagedetector': ['profiles/*.pk'],
    },
)
