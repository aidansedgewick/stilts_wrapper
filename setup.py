from setuptools import setup, find_packages

setup(
        name="stilts_wrapper",
        version="0.1.0",
        description="Thin wrapper around astro STILTS",
        url="https://github.com/aidansedgewick/stilts_wrapper",
        author="aidan-sedgewick",
        author_email='aidansedgewick@gmail.com',
        license="MIT license",
        #install_requires=requirements,
        packages = find_packages(),
        include_package_data=True,
        package_data={'': ['configuration/*.yaml']},
)

