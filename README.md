# cvmfs
Scripts to build the CVMFS repository for IceCube/WIPAC.

## Current Build

Inside the correct OS environment (possibly inside a container), run the following:

Build the base software:
`spack/build_v2.py py3-v4.3.0 --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org`

Build icetray metaprojects
`spack/build_v2.py py3-v4.3.0-metaproject --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org`

Done!


## Generic Build Instructions

### Spack Build

Build a single variant:

`spack/build_v2.py py3-v4.3.0 --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org`

Note that there are two build scripts. v2 applies for py3-v4.3.0 and later.

### System Dependencies

* gcc, make, autoconf (standard build system)
* git
* python

### Old Build

<details>
  <summary>py2 builds</summary>

  To build all variants at once:

  `cd builders;./build.py --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org`

  Or you can select a variant to build:

  `cd builders;./build.py --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org --variant py2_v2_base`

</details>
