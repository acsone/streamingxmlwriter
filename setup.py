# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV
# License LGPLv3 (http://www.gnu.org/licenses/lgpl-3.0-standalone.html)

from setuptools import setup

setup(
    name="streamingxmlwriter",
    version="1.0.1.dev1",
    description="A lightweight pythonic standard compliant "
                "streaming xml writer",
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    packages=["streamingxmlwriter"],
    install_requires=["six"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license='LGPLv3',
    author='ACSONE SA/NV',
    author_email='info@acsone.eu',
    url='http://github.com/acsone/streamingxmlwriter',
)
