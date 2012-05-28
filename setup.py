from distutils.core import setup

setup(
    name="plop",
    packages=["plop", "plop.test"],
    package_data={
        "plop.test": ["testdata/tornado_tests.pstats"],
        }
    )
