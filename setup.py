from pathlib import Path

from setuptools import find_packages, setup


setup(
    name='opera_coverage',
    use_scm_version=True,
    description='Calculate spatial-temporal coverage',
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',

    url='TBD',

    author='Angela Cheng, Karthik V., Charlie Marshak',
    author_email='angelviolinist718@gmail.com',

    keywords='opera',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],

    python_requires='>=3.10',

    install_requires=[
        'geopandas',
        'asf_search',
        'pandas',
        'matplotlib',
        'datetime',
        'pystac-client'
    ],

    extras_require={
        'develop': [
            'flake8',
            'flake8-import-order',
            'flake8-blind-except',
            'flake8-builtins',
            'pytest',
            'pytest-cov',
        ]
    },

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)