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

### Editing a Spack Build

There is a base file, then extensions for `-compiler`, `-pip`, and `-metaproject`.

A regular build will look for `-compiler` first, and if found will build all
projects with that compiler.  Then it will build all the packages specified in
the base file.  Finally it will run `pip install -r` on the `-pip` file.

A metaproject build with the `-metaproject` file specified will build icetray
metaprojects into the base build (must be performed after the base build is
successful).

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
