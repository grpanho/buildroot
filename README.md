# Operating Systems Laboratory (CC)

## Practical Work 1

### Guide

1. Objectives
    1. Expand knowledge about the construction and support of Linux distributions.
    2. Implementation and installation of a Web server.
    3. Learning about the content of the /proc directory.

2. Description

    The implementation of this work consists of generating a Linux distribution that has a WEB server written in Python or C/C++. To do so, it will be necessary to add a Python interpreter in the generated distribution (if Python is used), implement a WEB server, and write a simple HTML page.

    Support for the Python language can be added through the menuconfig of Buildroot (Interpreter languages and scripting submenu). However, Python requires a toolchain that supports WCHAR (a type of variable used for UTF-16 string encoding). This support can also be added through menuconfig. It will be necessary to recompile the entire distribution (make clean, followed by make). If C/C++ is used, the cross-compiler created by Buildroot itself can be used to compile the application.

    The objective of the HTML page is to provide basic information about the system's operation (target). Below is the list of information that should be presented on the page dynamically:

    * System date and time;
    * Uptime (time of operation without system restart) in seconds;
    * Processor model and speed;
    * Occupied capacity of the processor (%);
    * Total and used RAM memory (MB);
    * System version;
    * List of running processes (pid and name).
