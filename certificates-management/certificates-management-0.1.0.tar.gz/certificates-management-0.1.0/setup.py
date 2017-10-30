from setuptools import setup, find_packages

setup(
    name                    = "certificates-management",
    version                 = "0.1.0",
    description             = "Certificates Management tool",
    packages                = find_packages(),
    include_packages_data   = True,
    scripts                 = [""],
    install_requirements    = ["Flask==0.12.2",
                                "Flask-SQLAlchemy==2.3.2",
                                "Jinja2==2.9.6",
                                "SQLAlchemy==1.1.14",
                                "click==6.7",
                                "itsdangerous==0.24",
                                "MarkupSafe==1.0",
                                "Werkzeug==0.12.2"]
)