# CREATE SYSTEM #

This program simplifies the creation of linux environment for chroot systems.
It was designed with the Blusens'WebTV device in mind, but can be useful for
other systems, like android chroot environments.

It greatly simplifies the creation of the environment because the developer
only needs to specify the binaries, and it will include automagically all the
needed shared libraries. Then, just add other static files (like the folders
at /usr/share/program_name) and you should have everything needed to launch
your chroot environment with the bare minimum needed.

## USING CREATE_SYSTEM ##

Create_system uses a configuration file. Here is an example:

    system_path : /final_system/bg_apps

    binary: /bin/bash
    binary: /bin/busybox
    binary: /usr/bin/transmission-daemon3
    copy: /usr/share/transmission
    copy: /init
    copy: /lib/libm.so.6
    touch: /no_base_system
    link: /bin/ls busybox
    link: /bin/cp busybox
    link: /bin/telnetd busybox

 * *system_path* defines where to generate the environment. The default value is */final_system/bg_apps*, which is a suitable value for the WebTV system
 * *binary* specifies one binary to add to the final system. Create_system will
 also add all the libraries needed by it (using **ldd** to discover them). Of
 course, it can't detect libraries loaded in execution time.
 * *copy* will copy a file or a folder (recursively) *as is* to the destination
 system. Useful to copy the data in */usr/share*
 * *touch* creates an empty file in the destination system
 * *link* creates a symbolic link in the destination system called as the first
 parameter, and pointing to the second one *as is*

Create_system must be launch from a complete original system, using a chroot jail or a
container. Remember that you can use qemu to easily run non-x86 code in your PC.
To do so, just copy the *qemu-arch-static* executable to the */usr/bin* folder
in your full environment (being *arch* the architecture of your target system)
and launch the container or chroot environment as usual. Once inside, you can
run *create_system.py* to generate the definitive environment that you will copy
to the physical devide.

## CONTACTING THE AUTHOR ##

Sergio Costas
http://www.rastersoft.com
raster@rastersoft.com
rastersoft@gmail.com