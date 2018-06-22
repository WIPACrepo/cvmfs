#!/bin/sh

# from bash or tcsh, call this script as:
# eval `/cvmfs/icecube.opensciencegrid.org/setup.sh`

# SROOTBASE is the directory where this script lives
DIR=$(echo "${0%/*}")
if [ -d ${DIR} ]; then
    SROOTBASE=$(cd "$DIR" && echo "$(pwd -L)")
else
    SROOTBASE=$(pwd)
fi

# set operating system variables DISTRIB, VERSION, ARCH, and OS_ARCH
. $SROOTBASE/os_arch.sh >/dev/null

# VARS is the list of variables to be exported to the user's environment
#
VARS="SROOTBASE SROOT OS_ARCH PATH LD_LIBRARY_PATH"

# set the architecture-specific root directory
SROOT=$SROOTBASE/$OS_ARCH

# prepend the standard binary directory to the user's PATH
sroot_bin=$SROOT/bin
if [ "" = "$PATH" ]; then
    PATH="$sroot_bin"
else
    PATH="$sroot_bin:$PATH"
fi

# prepend the standard library directory to the user's LD_LIBRARY_PATH
sroot_lib=$SROOT/lib
if [ "" = "$LD_LIBRARY_PATH" ]; then
    LD_LIBRARY_PATH="$sroot_lib"
else
    LD_LIBRARY_PATH="$sroot_bin:$LD_LIBRARY_PATH"
fi

# initialize I3_DATA variable
sroot_data=$SROOTBASE/../data
if [ -d "$sroot_data" ]; then
    I3_DATA=${sroot_data}
    VARS="$VARS I3_DATA"

    # initialize I3_TESTDATA variable
    sroot_tstdata=$sroot_data/i3-test-data
    if [ -d ${sroot_tstdata} ]; then
        I3_TESTDATA=${sroot_tstdata}
        VARS="$VARS I3_TESTDATA"
    fi
fi

# add SROOT package configuration directory if it exists
sroot_pcfg=$SROOT/lib/pkgconfig
if [ -d ${sroot_pcfg} ]; then
    if [ "" = "$PKG_CONFIG_PATH" ]; then
        PKG_CONFIG_PATH="$sroot_pcfg"
    else
        PKG_CONFIG_PATH="$sroot_pcfg:$PKG_CONFIG_PATH"
        VARS="$VARS PKG_CONFIG_PATH"
    fi
fi

# ROOT specific bits
ROOTSYS=$SROOT
VARS="$VARS ROOTSYS"

# GotoBLAS
GOTO_NUM_THREADS=1
VARS="$VARS GOTO_NUM_THREADS"

# Globus
GLOBUS_LOCATION=${SROOT}
VARS="$VARS GLOBUS_LOCATION"
tmp_cert=${SROOT}/share/certificates
if [ -d ${tmp_cert} ]; then
    X509_CERT_DIR=${tmp_cert}
    VARS="$VARS X509_CERT_DIR"
fi

# export fully-qualified X509 user proxy environment variable
if [ ! -z "$X509_USER_PROXY" ]; then
    RET=`basename "$X509_USER_PROXY"`
    if [ "$RET" = "$X509_USER_PROXY" ]; then
        # if X509_USER_PROXY is just a filename, qualify it
        X509_USER_PROXY=$(pwd)/$X509_USER_PROXY
    fi
    if [ -d ${X509_USER_PROXY} ]; then
        VARS="$VARS X509_USER_PROXY"
    fi
fi


# start specialized detection, using python scripts
srootpy='python -E -s'

for var in PERL5LIB MANPATH; do
    varlower=`echo ${var} | tr '[:upper:]' '[:lower:]'`
    tmp=`${srootpy} ${SROOTBASE}/setup/${varlower}.py`
    if [ "" != "${tmp}" ]; then
        eval $var=\$tmp
        VARS="$VARS ${var}"
    fi
done

tmp=`${srootpy} ${SROOTBASE}/setup/opencl_libs.py`
if [ "" != "${tmp}" ]; then
    tmpocl=`echo ${tmp} | cut -d';' -f 1`
    tmplib=`echo ${tmp} | cut -d';' -f 2`
    if [ "" != "$tmpocl" ]; then
        OPENCL_VENDOR_PATH="${tmpocl}"
        VARS="$VARS OPENCL_VENDOR_PATH"
    fi
    if [ "" != "$tmplib" ]; then
        LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${tmplib}"
    fi
fi

# dump the final list of environment variables
CUR_SHELL=`readlink "/proc/$$/exe"|awk -F'/' '{print $NF}'`
for name in ${VARS}
do
  eval VALUE=\$$name
  case ${CUR_SHELL} in
        tcsh)
            echo 'setenv '$name' '\"$VALUE\"' ;' ;;
        csh)
            echo 'setenv '$name' '\"$VALUE\"' ;' ;;
        *)
            echo 'export '$name=\"$VALUE\"' ;' ;;
    esac
done
