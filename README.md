# Operating Systems Laboratory (CC)

# Assignment 1: Building and supporting Linux distributions

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

3. Build and Run

The following is a guide to set up and compile Buildroot, a Linux operating system building project. The guide includes instructions on how to download, configure, and compile Buildroot, as well as run it using QEMU. It also provides examples of custom configuration scripts that can be used to set up host and client communication.

## Getting Buildroot

For the latest version:

```bash
$ git clone git://git.buildroot.net/buildroot
```

For a tested version:

```bash
$ wget https://buildroot.org/downloads/buildroot-2023.02.tar.gz
$ tar -xvf buildroot-2023.02.tar.gz
```

## Configure Buildroot

### QEMU

```bash
$ make qemu_x86_defconfig
```

### menuconfig

```bash
$ make menuconfig
```

Inside menuconfig, modify the following configurations:

```
Toolchain  --->
		C library (uClibc-ng) ---> uClibc-ng
		[*] Enable C++ support
		[*] Enable WCHAR support

System configuration  --->
		()  Network interface to configure through DHCP
		[*] Run a getty (login prompt) after boot  --->
		  	(console) TTY port
		(custom-scripts/pre-build.sh) Custom scripts to run before creating filesystem images

Filesystem images  --->
		(250M) exact size

Target packages  --->
		Interpreter languages and scripting  --->
				[*] python3
				core python3 modules  --->
						[*] zlib module
				External python modules  --->
						[*] python-flask                                                                                                     
						[*] python-flask-babel                                                                                                
						[*] python-flask-cors
						[*] python-flask-expects-json
						[*] python-flask-jsonrpc
						[*] python-flask-login
						[*] python-flask-smorest
						[*] python-flask-sqlalchemy
						[*] python-flask-wtf
```

### linux-menuconfig

```bash
$ make linux-menuconfig
```

Inside linux-menuconfig, modify the following configurations:

```
Device Drivers  --->
		[*] Network device support  --->
				[*] Ethernet driver support  --->
				<*> Intel(R) PRO/1000 Gigabit Ethernet support
```

## Scripts Used

Inside `buildroot` run:

```bash
$ mkdir custom-scripts
```

And then, create a file in the new directory named `qemu-ifup`:

```bash
#!/bin/sh
set -x

switch=br0

if [ -n "$1" ];then
        ip tuntap add $1 mode tap user `whoami` # create tap network interface
        ip link set $1 up				                 # bring interface tap up
        sleep 0.5s					                      # wait the interface come up.
        sysctl -w net.ipv4.ip_forward=1         # allow forwarding of IPv4
				 route add -host 192.168.1.10 dev $1     # add route to the client
        exit 0
else
        echo "Error: no interface specified"
        exit 1
fi
```

Give it execution permission running the following:

```bash
$ chmod +x custom-scripts/qemu-ifup
```

Add another file called `S41network-config`:

```bash
#!/bin/sh
#
# Configuring host communication.
#

case "$1" in
  start)
	printf "Configuring host communication."
	
	/sbin/ifconfig eth0 192.168.1.10 up
	/sbin/route add -host **<HOST-IP>** dev eth0
	/sbin/route add default gw **<HOST-IP>**
	[ $? = 0 ] && echo "OK" || echo "FAIL"
	;;
  stop)
	printf "Shutdown host communication. "
	/sbin/route del default
	/sbin/ifdown -a
	[ $? = 0 ] && echo "OK" || echo "FAIL"
	;;
  restart|reload)
	"$0" stop
	"$0" start
	;;
  *)
	echo "Usage: $0 {start|stop|restart}"
	exit 1
esac

exit $?
```

Inside `custom-scripts` create a directory called `webserver`. 

Inside `webserver` create a file named `[main.py](http://main.py)`, a directory called `templates` and inside `templates` a file named `index.html`. 

It must be: `custom-scripts/webserver/main.py` and `custom-scripts/webserver/templates/index.html`

The contents of the files are shown below:

### main.py

```python
from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Get system date and time
    system_time = os.popen('date').read().strip()
    
    # Get server uptime
    uptime_output = os.popen('uptime').read().strip()
    uptime_parts = uptime_output.split('up ')
    uptime_data = uptime_parts[1].split(',')
    server_uptime = uptime_data[0].strip()

    # Get processor model and speed
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('model name'):
                cpu_model = line.split(':')[1].strip()
            elif line.startswith('cpu MHz'):
                cpu_speed = line.split(':')[1].strip()

    # Get processor load percentage
    with open('/proc/loadavg', 'r') as f:
        cpu_load = f.readline().split()[0]

    # Get memory usage
    mem_output = os.popen('free -h').read().strip().split('\n')
    mem_total  = mem_output[1].split()[1]
    mem_used   = mem_output[1].split()[2]
    mem_free   = mem_output[1].split()[3]
    mem_shared = mem_output[1].split()[4]
    mem_cached = mem_output[1].split()[5]

    # Get system version
    with open('/etc/os-release', 'r') as f:
        for line in f:
            if line.startswith('PRETTY_NAME'):
                system_version = line.split('=')[1].strip().strip('"')

    # Get list of processes with pid and name
    processes = []
    for filename in os.listdir('/proc'):
        if filename.isdigit():
            with open(f'/proc/{filename}/comm', 'r') as f:
                name = f.readline().strip()
            processes.append((filename, name))

    return render_template('index.html', system_time=system_time, server_uptime=server_uptime, cpu_model=cpu_model,
                           cpu_speed=cpu_speed, cpu_load=cpu_load, mem_used=mem_used, mem_total=mem_total, mem_free=mem_free, mem_shared=mem_shared,
                           mem_cached=mem_cached, system_version=system_version, processes=processes)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.10', port=80)
```

### index.html

```html
<!doctype html>
<html>
<head>
    <title>System Information</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <link rel="shortcut icon" href="https://cdn.imgbin.com/7/14/8/imgbin-penguin-tux-linux-penguins-4kX2P9dvq9ny0v6t6qjvYdzfh.jpg">
</head>
<body>
    <div class="container mt-5">
        <h1>System Information</h1>
        <p>System time: {{ system_time }}</p>
        <p>Server uptime: {{ server_uptime }}</p>
        <p>CPU model: {{ cpu_model }}</p>
        <p>CPU speed: {{ cpu_speed }} MHz</p>
        <p>CPU load: {{ cpu_load }}</p>
        <p>Memory usage: {{ mem_used }} / {{ mem_total }}</p>
        <p>Memory free: {{ mem_free }}</p>
        <p>Memory shared: {{ mem_shared }}</p>
        <p>Memory cached: {{ mem_cached }}</p>
        <p>System version: {{ system_version }}</p>
        <h2>List of Processes</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>PID</th>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>
                {% for pid, name in processes %}
                    <tr>
                        <td>{{ pid }}</td>
                        <td>{{ name }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>
</html>
```

Finally, add a file named `[pre-build.sh](http://pre-build.sh)`, it will copy the above files inside buildroot filesystem:

```bash
#!/bin/sh

cp $BASE_DIR/../custom-scripts/S41network-config $BASE_DIR/target/etc/init.d
chmod +x $BASE_DIR/target/etc/init.d/S41network-config

cp -r $BASE_DIR/../custom-scripts/webserver/* $BASE_DIR/target/root
```

Give it execution permission as well:

```bash
$ chmod +x custom-scripts/pre-build.sh
```

## Compile Buildroot

```bash
$ make
```

## Run Buildroot VM

**Remember to run inside buildroot directory!**

```bash
$ sudo apt-get install qemu-system
$ sudo qemu-system-i386 --device e1000,netdev=eth0,mac=aa:bb:cc:dd:ee:ff \
	--netdev tap,id=eth0,script=custom-scripts/qemu-ifup \
	--kernel output/images/bzImage \
	--hda output/images/rootfs.ext2 \
	--nographic \
	--append "console=ttyS0 root=/dev/sda"
```

## Run and Test Webserver

Inside `/root` run:

```bash
python3 main.py
```

If everything went right, you should access from the host machine at [http://192.168.1.10](http://192.168.1.10/) or any othe IP you have configured at the guest.
