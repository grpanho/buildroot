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

