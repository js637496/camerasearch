import json
import time
from multiprocessing.pool import ThreadPool as Pool
import subprocess as sp

pool_size = 100
pool = Pool(pool_size)
count = 0

def worker(url,count,id,polyArr):
    sp.run(["python3", "scaleInstance.py", url, str(count), id, str(polyArr)])



with open('nypoly.json') as json_file:
    data = json.load(json_file)
    for p in data['data']:
        count = count + 1
        #print('Name: ' + p['cameraID'])
        pool.apply_async(worker, (p['streamSource'],str(count),p['cameraID'],p['poly']))

pool.close()
pool.join()