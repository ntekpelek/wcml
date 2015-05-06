#! /bin/sh
RDIR=/mnt/ramdisk/wcml-lb-volatile # ramdisk dir
SDIR=/root/wcml-lb # static ( non-volatile ) dir
mkdir $RDIR
cd $RDIR
lb config --archive-areas "main contrib non-free" --bootappend-live "boot=live components persistence"
cp $SDIR/config/apt/preferences config/apt
cp $SDIR/config/package-lists/wcml.list.chroot config/package-lists
cp -R $SDIR/config/includes.chroot/opt config/includes.chroot/
cp -R $SDIR/config/includes.chroot/etc config/includes.chroot/
cp $SDIR/config/hooks/9001-enable-wcml-services.hook.chroot config/hooks/




