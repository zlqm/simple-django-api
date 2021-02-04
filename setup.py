import setuptools

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='simple_django_api',
    version='1.0.0',
    author='Abraham',
    author_email='abraham.liu@hotmail.com',
    description='django simple api',
    install_requires=[
        'django',
    ],
    extras_require={
        'jwt': ['PyJWT'],
    },
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
