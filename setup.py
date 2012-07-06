from distutils.core import setup

setup(
    name="plop",
    packages=["plop", "plop.test"],
    package_data={
        "plop": [
            "templates/index.html",
            "templates/force.html",
            "static/force.js",
            "static/third_party/d3/d3.v2.js",
            ],
        }
    )
