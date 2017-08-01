#!/bin/sh

# from bash or tcsh, call this script as:
# eval `/cvmfs/icecube.opensciencegrid.org/setup.sh`

##
# Functions
##

# return 0 if the second argument is not a member of the list in
# the first argument.  The third argument is ":" for paths, " " otherwise
listContains() {
    case "$3$1$3" in
	*"$3$2$3"*) return 0;;
    esac
    return 1
}

# if the second argument is not in the first argument's list, whose elements
# are separated by the character specified in the third argument.
# add it to the back if the fourth argument is "after", otherwise add it to
# the front
modifyList() {
    list="$1"
    new="$2"
    if [ -z ${3} ]; then
	sep=" "
    else
	sep=${3}
    fi
    key="$4"

    #echo "VAR \"$list\" NEW \"$new\" SEP \"$sep\" KEY \"$key\"" >&2

    if listContains "$list" "$new" "$sep"; then
	echo $list
	#echo $list   "# one" >&2
	return 0
    fi

    if [ -z "$list" ]; then
	echo $new
	#echo $new   "# two" >&2
	return 0
    fi

    if [ "$key" = "before" ]; then
	echo "$new$sep$list"
	#echo "$new$sep$list"   "# before" >&2
    else
	echo "$list$sep$new"
	#echo "$list$sep$new"   "# after" >&2
    fi
    return 0
}

# append the second argument to the path list
appendPath() {
    modifyList ${1} ${2} ":"
}

# prepend the second argument to the path list
prependPath() {
    modifyList ${1} ${2} ":" before
}

# find the architecture-specific Java executable
findJava() {
    echo "OS_ARCH \"$OS_ARCH\"" >&2
    case $OS_ARCH in
	RHEL_6_x86_64)
	    LIST="/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.33.x86_64
                  /usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64
                  /usr/lib/java"
	    ;;
	RHEL_5_i686) LIST=/usr/java/jdk1.5.0_12   ;;
	RHEL_5_x86_64) LIST=/usr/java/default     ;;
	RHEL_4_i686) LIST=/usr/java/j2sdk1.4.2_14 ;;
	RHEL_4_x86_64) LIST=/usr/java/j2sdk1.4.2  ;;
	Ubuntu_16.04_x86_64)
	    LIST=/usr/lib/jvm/java-8-openjdk-amd64/jre
	    ;;
	*) LIST=                                  ;;
    esac

    # look through the list for a valid directory
    for dir in $LIST; do
	if [ -d ${dir} ]; then
	    echo $dir
	    return 0
	fi
    done
}

##
# Code starts here
##

# SROOTBASE is the directory where this script lives
DIR=$(echo "${0%/*}")
if [ -d ${DIR} ]; then
    SROOTBASE=$(cd "$DIR" && echo "$(pwd -L)")
else
    SROOTBASE=$(pwd)
fi

# is this the py2 or py3 version?
case "$SROOTBASE" in
    *"py2-v"*) _version=2;;
    *"py3-v"*) _version=3;;
    *)
	echo "$0: Can't set version for path \"$0\"" >&2
	exit 1
esac

# set operating system variables DISTRIB, VERSION, ARCH, and OS_ARCH
. $SROOTBASE/os_arch.sh

# VARS is the list of variables to be exported to the user's environment
#
VARS="SROOTBASE OS_ARCH"

# set the architecture-specific root directory
SROOT=$SROOTBASE/$OS_ARCH

# if the binary or library directory doesn't exist, surrender to nihilism
sroot_bin=$SROOT/bin
sroot_lib=$SROOT/lib
if [ ! -d ${sroot_bin} ]; then
    echo "$0: Binary directory \"$sroot_bin\" doesn't exist" >&2
    exit 1
else
    if [ ! -d ${sroot_lib} ]; then
	echo "$0: Library directory \"$sroot_lib\" doesn't exist" >&2
	exit 1
    fi
fi

# prepend the standard binary directory to the user's PATH
PATH=$(prependPath "$PATH" "$sroot_bin")
VARS=$(modifyList "$VARS" "PATH")

# prepend the standard library directory to the user's LD_LIBRARY_PATH
LD_LIBRARY_PATH=$(prependPath "$LD_LIBRARY_PATH" "$sroot_lib")
VARS=$(modifyList "$VARS" "LD_LIBRARY_PATH")

# check for SROOT Python site packages
sroot_ppkg=$SROOT/lib/python2.7/site-packages
if [ -d ${sroot_ppkg} ]; then
    PYTHONPATH=$(prependPath "$PYTHONPATH" "$sroot_ppkg")
    VARS=$(modifyList "$VARS" "PYTHONPATH")
fi

# initialize I3_PORTS variable
sroot_ports=$SROOT/i3ports
if [ -d "$sroot_ports" ]; then
    I3_PORTS=${sroot_ports}
    VARS=$(modifyList "$VARS" "I3_PORTS")

    # add I3_PORTS library to LD_LIBRARY_PATH
    i3p_plib=$sroot_ports/lib
    if [ -d ${i3p_plib} ]; then
	LD_LIBRARY_PATH=$(prependPath "$LD_LIBRARY_PATH" "$i3p_plib")
	VARS=$(modifyList "$VARS" "LD_LIBRARY_PATH")

	# add I3_PORTS Python library to PYTHONPATH
	i3p_ppkg=$i3p_plib/python2.7/site-packages
	if [ -d ${i3p_ppkg} ]; then
	    PYTHONPATH=$(prependPath "$PYTHONPATH" "$i3p_ppkg")
	    VARS=$(modifyList "$VARS" "PYTHONPATH")
	fi
    fi
fi

# initialize I3_DATA variable
sroot_data=$SROOTBASE/../data
if [ -d "$sroot_data" ]; then
    I3_DATA=${sroot_data}
    VARS=$(modifyList "$VARS" "I3_DATA")

    # initialize I3_TESTDATA variable
    sroot_tstdata=$sroot_data/i3-test-data
    if [ -d ${sroot_tstdata} ]; then
	I3_TESTDATA=${sroot_tstdata}
	VARS=$(modifyList "$VARS" "I3_TESTDATA")
    fi
fi

# add SROOT package configuration directory if it exists
sroot_pcfg=$SROOT/lib/pkgconfig
if [ -d ${sroot_pcfg} ]; then
    PKG_CONFIG_PATH=$(prependPath "$PKG_CONFIG_PATH" "$sroot_pcfg")
    VARS=$(modifyList "$VARS" "PKG_CONFIG_PATH")
fi

# prepend SROOT Perl libraries to PERL5LIB
tmp_path=
for subdir in perl perl5 perl5/site_perl; do
    tmp_dir="$SROOT/lib/$subdir"
    if [ -d ${tmp_dir} ]; then
	tmp_path=$(appendPath "$tmp_path" "$tmp_dir")
    fi
done
if [ ! -z ${tmp_path} ]; then
    PERL5LIB=$(prependPath "$PERL5LIB" "$tmp_path")
    VARS=$(modifyList "$VARS" "PERL5LIB")
fi

# prepend SROOT manual page directories to MANPATH
tmp_path=
for subdir in man share/man; do
    tmp_dir="$SROOT/$subdir"
    if [ -d ${tmp_dir} ]; then
	tmp_path=$(appendPath "$tmp_path" "$tmp_dir")
    fi
done
if [ ! -z ${tmp_path} ]; then
    MANPATH=$(prependPath "$MANPATH" "$tmp_path")
    VARS=$(modifyList "$VARS" "MANPATH")
fi

# set GCC_VERSION environment variable
GCC_VERSION=`gcc -v 2>&1|tail -1|awk '{print $3}'`
VARS=$(modifyList "$VARS" "GCC_VERSION")

# ROOT specific bits
ROOTSYS=$SROOT
VARS=$(modifyList "$VARS" "ROOTSYS")

# GotoBLAS
GOTO_NUM_THREADS=1
VARS=$(modifyList "$VARS" "GOTO_NUM_THREADS")

# Java
if [ $_version -eq 2 ]; then
    tmp_home=${JAVA_HOME}
else
    tmp_home=$(findJava)
fi
if ([ -z ${tmp_home} ] || [ ! -f ${tmp_home}/bin/java ]); then
    # use SROOT Java
    tmp_home=${SROOTBASE}/../distrib/jdk1.6.0_24_$OS_ARCH
    if [ -d ${tmp_home} ]; then
        tmp_path=
        for subdir in lib jre/lib; do
            tmp_dir=${tmp_home}/${subdir}
            if [ -d ${tmp_dir} ]; then
		tmp_path=$(appendPath "$tmp_path" "$tmp_dir")
            fi
        done
        for archdir in amd64 i386; do
            for subdir in $archdir $archdir/server; do
                tmp_dir=${tmp_home}/jre/lib/$subdir
                if [ -d ${tmp_dir} ]; then
		    tmp_path=$(appendPath "$tmp_path" "$tmp_dir")
                fi
            done
        done

        if [ ! -z ${tmp_path} ]; then
            JAVA_HOME=${tmp_home}
            VARS=$(modifyList "$VARS" "JAVA_HOME")

	    LD_LIBRARY_PATH=$(prependPath "$LD_LIBRARY_PATH" "$tmp_path")
            VARS=$(modifyList "$VARS" "JAVA_HOME")
        fi
    fi
fi

GLOBUS_LOCATION=${SROOT}
VARS=$(modifyList "$VARS" "GLOBUS_LOCATION")

tmp_cert=${SROOT}/share/certificates
if [ -d ${tmp_cert} ]; then
    X509_CERT_DIR=${tmp_cert}
    VARS=$(modifyList "$VARS" "X509_CERT_DIR")
fi

# export fully-qualified X509 user proxy environment variable
if [ ! -z "$X509_USER_PROXY" ]; then
    RET=`basename "$X509_USER_PROXY"`
    if [ "$RET" = "$X509_USER_PROXY" ]; then
	# if X509_USER_PROXY is just a filename, qualify it
	X509_USER_PROXY=$(pwd)/$X509_USER_PROXY
    fi
    if [ -d ${X509_USER_PROXY} ]; then
	VARS=$(modifyList "$VARS" "X509_USER_PROXY")
    fi
fi

# build a list of possible shared library locations
libdirlist=${LD_LIBRARY_PATH}
for subdir in /usr/lib /usr/lib64 /lib /lib64 /usr/lib/x86_64-linux-gnu; do
    if [ -d ${subdir} ]; then
	libdirlist=$(appendPath "$libdirlist" "$subdir")
    fi
done

# find OpenCL and GNU Fortran shared libraries
OLDIFS="$IFS"
IFS=:
for p in ${libdirlist}
do
    if [ $_version -eq 2 ]; then
	if [ -e ${p}/libOpenCL.so.1 ]; then
	    tmp_ocl=${p}/libOpenCL.so.1
	elif [ -e ${p}/libOpenCL.so ]; then
	    tmp_ocl=${p}/libOpenCL.so
	fi
    fi

    if [ -e ${p}/libgfortran.so.3 ]; then
	tmp_ftn=${p}/libgfortran.so.3
    fi
    # XXX should we also check "libgfortran.so"?
done
IFS="$OLDIFS"

# initialize OpenCL vendor path and set
found_icd=1
if ( [ ! -z ${OPENCL_VENDOR_PATH} ] && [ -d ${OPENCL_VENDOR_PATH} ] ); then
    vpath=${OPENCL_VENDOR_PATH}
else
    vpath=/etc/OpenCL/vendors
    if [ ! -d ${vpath} ]; then
        vpath=${SROOTBASE}/../distrib/OpenCL_${OS_ARCH}/etc/OpenCL/vendors
    fi
fi
if [ -d ${vpath} ]; then
    # XXX should this use ARCH to define the expected ICD name?
    if ( [ ! -e ${vpath}/amdocl64.icd ] && [ ! -e ${vpath}/intel64.icd ] )
    then
	# didn't find any installable client drivers
        found_icd=0
    fi

    OPENCL_VENDOR_PATH=${vpath}
    VARS=$(modifyList "$VARS" "OPENCL_VENDOR_PATH")
fi

# if no ICD files were found, use SROOT OpenCL
if ( [ -z ${tmp_ocl} ] || [ ${found_icd} -eq 0 ] ); then
    tmp_ocl=${SROOTBASE}/../distrib/OpenCL_${OS_ARCH}
    tmp_lib=${tmp_ocl}/lib/$OS_ARCH
    tmp_icd=${tmp_ocl}/etc/OpenCL/vendors

    if [ -d ${tmp_lib} ]; then
	LD_LIBRARY_PATH=$(prependPath "$LD_LIBRARY_PATH" "$tmp_lib")
	VARS=$(modifyList "$VARS" "LD_LIBRARY_PATH")
    fi

    if [ $_version -eq 2 ]; then
	if [ "${OPENCL_VENDOR_PATH}" = "/etc/OpenCL/vendors" -a -d ${tmp_icl} ]
	then
	    # copy all ICD files into a single directory
            OPENCL_VENDOR_PATH=`mktemp -d 2>/dev/null || mktemp -d -t 'vendortmp'`
            cp -r /etc/OpenCL/vendors/* ${OPENCL_VENDOR_PATH}
            cp -r ${tmp_icd}/* ${OPENCL_VENDOR_PATH}
	    VARS=$(modifyList "$VARS" "OPENCL_VENDOR_PATH")
	fi
    fi
fi

# if we didn't find a shared GNU Fortran library, try a different location
if [ -z ${tmp_ftn} ]; then
    tmp_ftn="$SROOT/tools/gfortran"
    if [ -d ${tmp_ftn} ]; then
	LD_LIBRARY_PATH=$(appendPath "$LD_LIBRARY_PATH" "$tmp_ftn")
	VARS=$(modifyList "$VARS" "LD_LIBRARY_PATH")
    fi
fi

# dump the final list of environment variables
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
