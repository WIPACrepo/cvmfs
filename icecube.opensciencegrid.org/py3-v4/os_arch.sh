#!/bin/sh

if [ -x /usr/bin/lsb_release ]; then
    DISTRIB=`lsb_release -si|tr '[:upper:]' '[:lower:]'`
    VERSION=`lsb_release -sr`
    if [ "$VERSION" = "n/a" ]; then
        VERSION=`lsb_release -sc`
    fi
elif [ -e /etc/os-release ]; then
    DISTRIB=`cat /etc/os-release|grep '^ID='|cut -d '=' -f 2|sed s/\"//g|tr '[:upper:]' '[:lower:]'`
    VERSION=`cat /etc/os-release|grep '^VERSION='|cut -d '=' -f 2|cut -d ' ' -f 1|sed s/\"//g`
    if [ "x$VERSION" = "x" ]; then
        VERSION=`cat /etc/os-release|grep '^VERSION.*='|cut -d '=' -f 2|cut -d ' ' -f 1|sed s/\"//g`
    fi
elif [ -e /etc/redhat-release ]; then
    DISTRIB="centos"
    VERSION=`cat /etc/redhat-release|sed s/\ /\\\\n/g|grep '\.'`
else
    DISTRIB=`uname -s|tr '[:upper:]' '[:lower:]'`
    VERSION=`uname -r`
fi
if [ "x$ARCH" = "x" ]; then
    ARCH=`uname -m`
fi

# detect optimizations
case $ARCH in
    "x86_64")
        ARCH=`awk 'BEGIN {
    while (!/flags/) if (getline < "/proc/cpuinfo" != 1) exit 1
    if (/lm/&&/cmov/&&/cx8/&&/fpu/&&/fxsr/&&/mmx/&&/syscall/&&/sse2/) level = 1
    if (level == 1 && /cx16/&&/lahf/&&/popcnt/&&/sse4_1/&&/sse4_2/&&/ssse3/) level = 2
    if (level == 2 && /avx/&&/avx2/&&/bmi1/&&/bmi2/&&/f16c/&&/fma/&&/abm/&&/movbe/&&/xsave/) level = 3
    if (level == 3 && /avx512f/&&/avx512bw/&&/avx512cd/&&/avx512dq/&&/avx512vl/) level = 4
    if (level > 0) { print "x86_64_v" level; exit level + 1 }
    exit 1
}'`
        ;;
    "aarch64")
        if cat /proc/cpuinfo | grep 'neon'; then
            ARCH='aarch64_neon'
        fi
        ;;
esac

# Map binary compatible operating systems and versions onto one another
case $DISTRIB in
    "redhatenterpriseclient" | "redhatenterpriseserver" | "redhatenterprise" | "rhel" | "scientificsl" | "scientific" | "centos" | "centosstream" | "scientificfermi" | "scientificcernslc" | "almalinux" | "rocky")
        DISTRIB="RHEL"
        VERSION=`echo "${VERSION}" | cut -d '.' -f 1`
        ;;
    "ubuntu" | "linuxmint")
        DISTRIB="Ubuntu"
        if echo $VERSION | grep -q '24\.\?'; then
            VERSION="24.04"
        elif echo $VERSION | grep -q '23\.\?'; then
            VERSION="22.04"
        elif echo $VERSION | grep -q '22\.\?'; then
            VERSION="22.04"
        elif echo $VERSION | grep -q '21\.\?'; then
            VERSION="20.04"
        elif echo $VERSION | grep -q '20\.\?'; then
            VERSION="20.04"
        elif echo $VERSION | grep -q '19\.\?'; then
            VERSION="18.04"
        elif echo $VERSION | grep -q '18\.\?'; then
            VERSION="18.04"
        elif echo $VERSION | grep -q '17\.\?'; then
            VERSION="16.04"
        elif echo $VERSION | grep -q '16\.\?'; then
            VERSION="16.04"
        elif echo $VERSION | grep -q '15\.10'; then
            VERSION="15.10"
        elif echo $VERSION | grep -q '15\.\?'; then
            VERSION="14.04"
        elif echo $VERSION | grep -q '14\.\?'; then
            VERSION="14.04"
        elif echo $VERSION | grep -q '13\.\?'; then
            VERSION="12.04"
        elif echo $VERSION | grep -q '12\.\?'; then
            VERSION="12.04"
        fi
        ;;
    "debian")
        DISTRIB="Ubuntu"
        if [ "$VERSION" = "unstable" ]; then
            VERSION="24.04"
        elif [ "$VERSION" = "testing" ]; then
            VERSION="24.04"
        elif [ "$VERSION" = "trixie" ]; then
            VERSION="24.04"
        elif echo $VERSION | grep -q '12\.\?'; then
            VERSION="22.04"
        elif echo $VERSION | grep -q '11\.\?'; then
            VERSION="20.04"
        elif echo $VERSION | grep -q '10\.\?'; then
            VERSION="18.04"
        elif echo $VERSION | grep -q '9\.\?'; then
            VERSION="16.04"
        elif echo $VERSION | grep -q '8\.\?'; then
            VERSION="14.04"
        fi
        ;;
    "freebsd")
        DISTRIB="FreeBSD"
        VERSION=`uname -r | cut -d '.' -f 1`
        ARCH=`uname -p`
        ;;
    "darwin")
        DISTRIB="OSX"
        VERSION=`uname -r | cut -d '.' -f 1`
        ;;
    "linux")
        # Damn. Try harder with the heuristics.
        if echo $VERSION | grep -q '\.el8\.\?'; then
            DISTRIB="RHEL"
            VERSION=8
        elif echo $VERSION | grep -q '\.el7\.\?'; then
            DISTRIB="RHEL"
            VERSION=7
        elif echo $VERSION | grep -q '\.el6\.\?'; then
            DISTRIB="RHEL"
            VERSION=6
        elif echo $VERSION | grep -q '\.el5\.\?'; then
            DISTRIB="RHEL"
            VERSION=5
        fi
esac

OS_ARCH=${DISTRIB}_${VERSION}_${ARCH}
echo ${OS_ARCH}
export OS_ARCH
