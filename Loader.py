#!/usr/bin/python3
import os
import socket
import subprocess
import logging
import time
import signal
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger()

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', int(port))) == 0

logger.info(f"--> CargoDeck Loader Started")

# Configure match string based on instance number
env_containername = os.getenv('CONTAINER_NAME', "CargoDeck")

instanceNumber = 1
# The first PORT may be specified as both PORT and PORT1.
if os.environ.get('PORT1') is None:
    os.environ['PORT1'] = os.getenv("PORT", "undefined")
    
# The first MATCH may be specified as both MATCH and MATCH1.
if os.environ.get('MATCH1') is None:
    os.environ['MATCH1'] = os.getenv("MATCH", env_containername)

subprocesses = []  # Keep track of the subprocesses here

env_worker = os.getenv("WORKERS", "1")
env_worker =  1 if not env_worker.isnumeric() else int(env_worker)
if int(env_worker) <  1:        env_worker =  1 
if int(env_worker) > 10:        env_worker = 10 

# Loop through PORTn...
while (env_port := os.getenv("PORT"+str(instanceNumber), None)) is not None:
    if not env_port.isnumeric():
        logger.error(f"Loader: PORT{str(instanceNumber)} must be a number, but is {env_port}")
        sys.exit(1)
    if not (1 <= int(env_port) <= 65535):
        logger.error(f"Loader: PORT{str(instanceNumber)} must be a number in the range 1-65535, but is {str(env_port)}")
        sys.exit(1)
    if is_port_in_use(env_port):
        logger.error(f"Loader: PORT {str(env_port)} is in use. Requested for PORT{str(instanceNumber)}")
        sys.exit(1)

    # Get MATCH to use. 
    env_match = os.getenv("MATCH"+str(instanceNumber), env_containername)

    # Copy current environment variables and update with specific values for this particular child.
    new_env = os.environ.copy()  
    new_env["PORT"] = str(env_port)
    new_env["MATCH"] = env_match
    new_env["CARGODECK_INSTANCE"] = str(instanceNumber)

    logger.info(f"Loader: Spawning instance {instanceNumber} on port '{env_port}'")
    #cmd = f"gunicorn -w 1 -b 0.0.0.0:{str(env_port)} CargoDeck:app"
    cmd = f"gunicorn -w {str(env_worker)} -k gevent -b 0.0.0.0:{str(env_port)} CargoDeck:app"
    logger.info(f"cmd = {cmd}")
    process = subprocess.Popen(cmd, shell=True, env=new_env)
    subprocesses.append( process )
    
    if not os.environ.get("INSTANCES", "") == "MULTI":
        logger.info(f"Loader: Multi-instances disabled.")
        break
    else:
        instanceNumber += 1
        time.sleep(0.5)  # Pause for 500 ms to try to ensure a nice startup log.

logger.info(f"Loader: Spawning has finished. Awaiting termination.")

def signal_handler(sig, frame):
    raise Exception("SIGTERM received")

signal.signal(signal.SIGTERM, signal_handler)
try:
    while True:
        time.sleep(1)
except:
    pass
finally:
    logger.info(f"Loader: Performing cleanup")
    for process in subprocesses:
        #process.terminate()
        process.kill()
    logger.info(f"Loader: Done")
