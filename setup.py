from setuptools import setup

setup(
    name="streamingxmlwriter",
    description="A lightweight pythonic standard compliant "
                "streaming xml writer",
    version="1.0.0",
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
