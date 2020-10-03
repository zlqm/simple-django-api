import setuptools

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='django_improved_view',
    version='1.0',
    author='Abraham',
    author_email='abraham.liu@hotmail.com',
    description='add some feature for django view and request',
    install_requires=['django'],
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
