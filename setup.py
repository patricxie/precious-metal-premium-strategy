from setuptools import setup, find_packages


setup(
    name="precious-metal-dashboard",
    version="0.1.0",
    description="Precious Metal Premium Strategy Dashboard",
    author="Patric Xie",
    py_modules=["run_dashboard", "dashboard_app"],
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "numpy",
        "matplotlib",
        "yfinance",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "precious-metal-dashboard=run_dashboard:main",
        ],
    },
)