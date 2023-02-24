from setuptools import setup

setup(
    name='pyAutoMark',
    version='0.3.0',    
    description='Automated marking of student electronic submissions',
    url='https://github.com/willijar/pyAutoMark',
    author='John Williams',
    author_email='j.a.r.williams@jarw.org.uk',
    license='GPL-3.0-Only',
    packages=['pyAutoMark'],
    install_requires=['openpyxl>=3.0',
                      'pytest>7.2.1',                     
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Academic/teaching', 
        'Operating System :: POSIX :: Linux',   
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: C',
        'Programming Language :: VHDL',
        'Framework :: Pytest',
        'Topic :: Education :: Testing',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
)