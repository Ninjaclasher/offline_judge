from setuptools import find_packages, Extension, setup


extensions = [Extension('offline_judge._checker', sources=['offline_judge/_checker.c'])]

with open('README.md') as f:
    readme = f.read()

setup(
    name='offline_judge',
    version='1.0.2',
    entry_points={
        'console_scripts': [
            'judge = offline_judge.judge:main',
        ],
    },
    ext_modules=extensions,
    author='Evan Zhang, jw4js',
    install_requires=['termcolor'],
    description='An offline equivalent of an online judge.',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/Ninjaclasher/offline_judge',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
)
