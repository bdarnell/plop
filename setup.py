from distutils.core import setup

setup(
    name="plop",
    version="0.1.1",
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
    )
