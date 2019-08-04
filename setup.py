from setuptools import setup, find_packages

with open('./requirements.txt') as reqs:
    requirements = [line.rstrip() for line in reqs]

setup(name="STAC Derivatives",
      version='0.1',
      author='Jeff Albrecht',
      author_email='geospatialjeff@gmail.com',
      packages=find_packages(exclude=['tests', 'lambda']),
      install_requires = requirements,
      entry_points= {
          "console_scripts": [
              "stac-derivatives=derivatives.scripts.cli:stac_derivatives"
          ]},
      include_package_data=True
      )