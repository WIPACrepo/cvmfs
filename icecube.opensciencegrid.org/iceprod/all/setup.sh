#!/bin/sh

# from bash or tcsh, call this script as:
# eval `/cvmfs/icecube.opensciencegrid.org/iceprod/current/setup.sh`

# This is here since readlink -f doesn't work on Darwin
DIR=$(echo "${0%/*}")
ICEPRODBASE=$(cd "$DIR" && echo "$(pwd -L)")

. $ICEPRODBASE/os_arch.sh >/dev/null

ICEPRODROOT=$ICEPRODBASE/$OS_ARCH

PATH=$ICEPRODROOT/bin:$PATH

PKG_CONFIG_PATH=$ICEPRODROOT/lib/pkgconfig:$PKG_CONFIG_PATH
LD_LIBRARY_PATH=$ICEPRODROOT/lib:$ICEPRODROOT/lib64:$LD_LIBRARY_PATH

python_version=$($ICEPRODROOT/bin/python -V|awk '{print $2}'|awk -F. '{print $1"."$2}')
PYTHONPATH="$ICEPRODROOT/lib/python${python_version}/site-packages"

MANPATH=$ICEPRODROOT/man:$ICEPRODROOT/share/man:$MANPATH
GLOBUS_LOCATION=$ICEPRODROOT
GLOBUS_GSSAPI_NAME_COMPATIBILITY="HYBRID"
X509_CERT_DIR=${ICEPRODROOT}/share/certificates
VOMS_USERCONF=${ICEPRODROOT}/etc/vomses
I3_DATA=$ICEPRODBASE/../../data

VARS="OS_ARCH ICEPRODBASE ICEPRODROOT PATH PYTHONPATH PKG_CONFIG_PATH LD_LIBRARY_PATH MANPATH GLOBUS_LOCATION GLOBUS_GSSAPI_NAME_COMPATIBILITY X509_CERT_DIR VOMS_USERCONF I3_DATA"

IFS=' '
for name in ${VARS}
do
  eval VALUE=\$$name
  case ${SHELL##*/} in
    tcsh)
        echo 'setenv '$name' '\"$VALUE\"' ;' ;;
    csh)
        echo 'setenv '$name' '\"$VALUE\"' ;' ;;
    *)
        echo 'export '$name=\"$VALUE\"' ;' ;;
  esac
done
