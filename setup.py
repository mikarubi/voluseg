import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

# with open('requirements.txt', 'r') as fh:
#     install_requires = fh.read().split('\n')

setuptools.setup(
    name='voluseg',
    version='2019.12',
    author='Mika Rubinov',
    author_email='mikarubi@gmail.com',
    description='pipeline for volumetric segmentation of calcium imaging data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikarubi/voluseg',
    packages= [
        'voluseg',
        'voluseg._steps',
        'voluseg._tools'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
    # install_requires=install_requires
)

