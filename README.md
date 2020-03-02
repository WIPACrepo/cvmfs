# cvmfs
Scripts to build the CVMFS repository for IceCube/WIPAC.

## Spack Build

Build a single variant:

`spack/build.py py3-v4.1.0 --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org`


## Old Build

To build all variants at once:

`cd builders;./build.py --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org`

Or you can select a variant to build:

`cd builders;./build.py --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org --variant py2_v2_base`
