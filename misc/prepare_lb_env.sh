#! /bin/sh
RDIR=/mnt/ramdisk/wcml-lb-volatile # ramdisk dir
LBDIR=/root/wcml/lb # static ( non-volatile ) dir
APPDIR=/root/wcml/wcml_webapp
W2PYDIR=/root/web2py
rm $W2PYDIR/routes.py
mkdir $RDIR
cd $RDIR
lb config --archive-areas "main contrib non-free" --bootappend-live "boot=live components persistence"
cp $LBDIR/config/apt/preferences config/apt
cp $LBDIR/config/package-lists/wcml.list.chroot config/package-lists
cp -R $LBDIR/config/bootloaders config/bootloaders
cp -R $LBDIR/config/includes.chroot/opt config/includes.chroot/
cp -R $W2PYDIR config/includes.chroot/opt/wcml
cp -R $LBDIR/config/includes.chroot/etc config/includes.chroot/
cp -R $LBDIR/config/includes.chroot/home config/includes.chroot/
cp $LBDIR/config/hooks/9001-enable-wcml-services.hook.chroot config/hooks/
cp -R $APPDIR config/includes.chroot/opt/wcml/web2py/applications/




