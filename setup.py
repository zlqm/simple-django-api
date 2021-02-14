import setuptools

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name='simple_django_api',
    version='1.0.3',
    author='Abraham',
    author_email='abraham.liu@hotmail.com',
    description='django simple api',
    install_requires=[
        'django',
    ],
    extras_require={
        'jwt': ['PyJWT'],
        'webargs': ['webargs'],
        'all': ['PyJWT', 'webargs'],
    },
    long_description=long_description,
    packages=setuptools.find_packages(),
    url='https://github.com/zlqm/simple_django_api',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
