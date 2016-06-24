import time

ip = '/mnt/girder_worker/data/input_pipe'
op = '/mnt/girder_worker/data/output_pipe'

# Reads lines from the input pipe, reverses them, then writes them to the output pipe.
# Sleeps for a short duration between each line.
with open(ip, 'r') as ifd, open(op, 'w') as ofd:
    for line in ifd:
        ofd.write(line[::-1])
        ofd.flush()
        time.sleep(0.4)
print '\nALL DONE!!'
