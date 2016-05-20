import random
import string
import time

with open('/mnt/girder_worker/data/my_named_pipe', 'wb') as fd:
    for i in range(15):
        fd.write(''.join(random.choice(string.ascii_letters + string.digits)
                 for x in range(random.randint(20, 100))))
        fd.flush()
        time.sleep(2)

