from distutils.core import setup

setup(
    name="plop",
    version="0.1.2",
    packages=["plop", "plop.test"],
    package_data={
        "plop": [
            "templates/index.html",
            "templates/force.html",
            "static/force.js",
            "static/third_party/d3/d3.v2.js",
            ],
        },
    author="Ben Darnell",
    url="https://github.com/bdarnell/plop",
    install_requires=[
	    "tornado",
    ],
 )
