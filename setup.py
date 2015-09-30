from setuptools import setup

setup(
    name="plop",
    version="0.3.0",
    packages=["plop", "plop.test"],
    package_data={
        "plop": [
            "templates/index.html",
            "templates/force.html",
            "templates/force-flat.html",
            "static/force.js",
            "static/styles.css"
            ],
        },
    author="Ben Darnell",
    url="https://github.com/bdarnell/plop",
    install_requires=[
        'tornado',
        'six',
    ],
    )
