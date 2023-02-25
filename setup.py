import setuptools

setuptools.setup(
    name='pyAutoMark',
    version='0.3.1',  
    python_requires='>3.6.0',  
    description='Automated marking of student electronic submissions',
    url='https://github.com/willijar/pyAutoMark',
    author='John Williams',
    author_email='j.a.r.williams@jarw.org.uk',
    license='GPL-3.0-Only',
    packages=['pyam','pyam.fixtures','pyam.cmd'],
    package_dir={'pyam':'pyam'},
    package_data={'pyam': ['*.xlsx']},
    install_requires=['openpyxl>=3.0',
                      'pytest>=7.2.1',                     
                      ],
    scripts=['pyam/pyAutoMark.py'],
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