from setuptools import setup, find_packages

requires = [
    'flask',
    'yeelight',
    'pyaudio',
    'aubio'
]

setup(
    name='yeelight-music-mode',
    version='0.1',
    description='Improved music mode for Yeelight color bulbs using PyAudio and Aubio libraries '
                'for audio processing', 
    author='Timothy Logan',
    author_email='timtimmahh@gmail.com',
    keywords='web flask pyaudio yeelight audio music',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires
)