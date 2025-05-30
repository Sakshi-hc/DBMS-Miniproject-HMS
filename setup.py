from setuptools import setup, find_packages

setup(
    name="hospital_management_system",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Login==0.6.3",
        "Flask-WTF==1.2.1",
        "PyMySQL==1.1.0",
        "python-dotenv==1.0.0",
        "Werkzeug==2.3.7",
        "email-validator==2.1.0.post1",
        "cryptography==41.0.3",
        "SQLAlchemy==1.4.46"
    ],
) 