Release checklist
- [ ] Check outstanding issues on JIRA and Github
- [ ] Check [latest documentation
](https://fastqsplitter.readthedocs.io/en/latest/) looks fine
- [ ] Create a release branch 
  - [ ] Set version to a stable number.
  - [ ] Change current development version in `CHANGELOG.rst` to stable version.
- [ ] Merge the release branch into `master`
- [ ] Create a test pypi package from the master branch. ([Instructions.](
https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives
))
    - [ ] Use `build-wheels.sh` to build the compiled C wheels.
- [ ] Install the packages from the test pypi repository to see if they work.
- [ ] Created an annotated tag with the stable version number. Include changes 
from CHANGELOG.rst.
- [ ] Push tag to remote.
- [ ] Push tested packages to pypi
- [ ] merge `master` branch back into `develop`.
- [ ] Add updated version number to develop
- [ ] Update the package on bioconda
- [ ] Build the new tag on readthedocs. Only build the last patch version of
each minor version. So `1.1.1` and `1.2.0` but not `1.1.0`, `1.1.1` and `1.2.0`.