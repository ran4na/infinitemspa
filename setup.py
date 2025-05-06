from setuptools import find_packages, setup 

setup( 
    name='tiny-bbs', 
    version='0.1', 
    description='', 
    author='', 
    author_email='', 
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'wheel',
        'Flask',
        'Flask-SQLAlchemy',
        'flask-bcrypt',
        'flask-login',
        'Flask-WTF',
        'markupsafe',
        'configparser',
        'filetype',
        'Pillow',    
        'qrcode',
        'WTForms-Alchemy',
        'bbcode'
    ]
)