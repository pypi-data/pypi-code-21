from setuptools import setup

setup(
    name="TBWW",
    version="0.1.1",
    description="Telegram Bot Wrapper Wraper",
    license="GNU GPL 3.0",
    install_requires=["python-telegram-bot"],
    entry_points={
        "console_scripts": [
            "tbww=tbww"
        ]
    }
)
