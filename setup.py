from setuptools import setup, find_packages

setup(
    name="syntient",
    version="0.1.0",
    description="A modular AI assistant platform",
    author="Syntient AI",
    author_email="syntient@example.com",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "flask",
        "requests",
    ],
    python_requires=">=3.8",
)
