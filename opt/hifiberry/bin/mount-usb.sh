#!/bin/bash

ACTION=$1
DEVBASE=$2
EXTRAARG=$3
DEVICE="/dev/${DEVBASE}"
BASEDIR=/mnt
UPPERDIR=/data/library/overlaydir
WORKDIR=/data/library/workdir
MUSICDIR=/data/library/music

# Make sure /data is mounted
/opt/hifiberry/bin/mount-data.sh

# See if this drive is already mounted
MOUNT_POINT=$(/bin/mount | /bin/grep ${DEVICE} | /usr/bin/awk '{ print $3 }')

do_mount()
{
    if [[ -n ${MOUNT_POINT} ]]; then
        # Already mounted, exit
        exit 1
    fi
	
    # Get info for this drive: $ID_FS_LABEL, $ID_FS_UUID, and $ID_FS_TYPE
    eval $(/sbin/blkid -o udev ${DEVICE} | grep -v " ")

    # It might have partitions, in this case, we'll use the first one
    if [ -f /dev/${DEVICE}1 ]; then
        DEVICE=${DEVICE}1
        echo $DEVICE
        eval $(/sbin/blkid -o udev $DEVICE | grep -v " ")
        env
    fi

    # Figure out a mount point to use
    # If there is a partition UUID, use this as it should be unique
    if [[ -z "${LABEL}" ]]; then
        LABEL=${ID_FS_PARTUUID}
    fi
    if [[ -z "${LABEL}" ]]; then
        LABEL=${ID_FS_UUID}
    fi
    # Otherwise try the label
    if [[ -z "${LABEL}" ]]; then
        LABEL=${ID_FS_LABEL}
    fi
    # still nothing? Use the device name
    if [[ -z "${LABEL}" ]]; then
        LABEL=${DEVBASE}
    elif /bin/grep -q " /media/${LABEL} " /etc/mtab; then
        # Already in use, make a unique one
        LABEL+="-${DEVBASE}"
    fi
    MOUNT_POINT="$BASEDIR/${LABEL}"

    /bin/mkdir -p ${MOUNT_POINT}

    # workaround
    if [ -f ${MOUNT_POINT}/noalbum ]; then
        rm  ${MOUNT_POINT}/noalbum
    fi

    # Global mount options
    OPTS="rw,relatime"
    OVERLAY=1

    # File system type specific mount options
    if [[ ${ID_FS_TYPE} == "vfat" ]]; then
        OPTS+=",users,gid=100,umask=000,shortname=mixed,utf8=1,flush"
	OVERLAY=0
    fi
  
     if [[ ${ID_FS_TYPE} == "ntfs" ]]; then
        OPTS+=" -t ntfs-3g"
        OVERLAY=0
    fi

    # Do not support overlays (for now)
    OVERLAY=0

    if [ -x /opt/hifiberry/bin/report-activation ]; then
        /opt/hifiberry/bin/report-activation mount_${ID_FS_TYPE}
    fi 

    if ! /bin/mount -o ${OPTS} ${DEVICE} ${MOUNT_POINT}; then
        # Error during mount process: cleanup mountpoint
        /bin/rmdir ${MOUNT_POINT}
        exit 1
    fi

    # Overlay mount if file system is supported
    if [ "$OVERLAY" == "1" ]; then
        echo "Creating overlay mount for ${MOUNT_POINT} /fstype ${ID_FS_TYPE}"
        mkdir -p $UPPERDIR
        mkdir -p $WORKDIR
        mkdir -p ${MUSICDIR}/${LABEL}
        CMD="mount -t overlay -o lowerdir=${MOUNT_POINT},upperdir=${UPPERDIR},workdir=${WORKDIR} overlay ${MUSICDIR}/${LABEL}"
        $CMD
        if [ $? != 0 ]; then
            echo $CMD failed
        fi
    else
        echo "Creating symlink as ${ID_FS_TYPE} does not support overlays"
        if [ -h ${MUSICDIR}/${LABEL}  ]; then
	    rm ${MUSICDIR}/${LABEL}
        fi
        if [ -a ${MUSICDIR}/${LABEL} ]; then
            mv ${MUSICDIR}/${LABEL} ${MUSICDIR}/../${LABEL}.bak
        fi
    
        ln -s ${MOUNT_POINT} ${MUSICDIR}/${LABEL}
    fi 


    # Rescan MPD
    if [ "$EXTRAARG" != "norescan" ]; then
	if [ -x /opt/hifiberry/bin/update-mpd-db ]; then
        	/opt/hifiberry/bin/update-mpd-db &
	fi
    fi

    # Just an echo to get a 0 return code
    echo "mounted  ${LABEL}"
            
}

do_unmount()
{
    if [[ -n ${MOUNT_POINT} ]]; then
        /bin/umount -l ${DEVICE}
        /bin/umount -l ${DEVICE}1
        echo "unmounted ${DEVICE}"
    fi
}
case "${ACTION}" in
    add)
        do_mount
        ;;
    remove)
        do_unmount
        ;;
esac
