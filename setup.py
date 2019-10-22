from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name='askomics',
    version='3.1.1',
    description='''
        AskOmics is a visual SPARQL query interface supporting both intuitive
        data integration and querying while shielding the user from most of the
        technical difficulties underlying RDF and SPARQL
    ''',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    maintainer='Xavier Garnier',
    maintainer_email='xavier.garnier@irisa.fr',
    url='https://github.com/askomics/flaskomics',
    keyword='rdf sparql query data integration',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
