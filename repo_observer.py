import argparse
import os
import socket
import subprocess
import time

import helpers

FORMAT = 'utf-8'

def poll ():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--dispatcher-server",
                        help="dispatcher host:port, " \
                        "by default it uses localhost:8888",
                        default="localhost:8888",
                        action="store")

    parser.add_argument("repo",metavar="REPO",type=str,
    help="path to the repository this will observe")
    args = parser.parse_args()
    dispatcher_host, disptacher_port = args.dispatcher_server.split(":")

    while True:
        try:
            #run shell script update_repo.sh with repo location
            subprocess.check_output(["./update_repo.sh",args.repo])
        except subprocess.CalledProcessError as e:
            raise Exception("Could not update and check repo. " + "Reason : %s" % e.output)
        #check if commit_id was generated
        if os.path.isfile(".commit_id"):
                try:
                    #get status of dispatch server
                    response = helpers.communicate(dispatcher_host.encode(FORMAT), 
                    int(disptacher_port),
                    "status".encode(FORMAT))
                except socket.error as e:
                    raise Exception("Could not communicate with dispatcher server: %s" %e)
                print("Notify dispatcher")
                if response.decode(FORMAT) == "OK":
                    
                    commit = ""
                    #read the commit id and send it to dispatch server
                    with open(".commit_id","r") as f:
                        commit = f.readline()
                    response = helpers.communicate(dispatcher_host.encode(FORMAT), int(disptacher_port), 
                    f"dispatch:{commit}".encode(FORMAT))

                    if response.decode(FORMAT) != "OK":
                        raise Exception("Could not dispatch the test: %s" %response)

                    print ("Dispatched!")
                
                else: 
                    raise Exception("Could not dispatch tests: %s" %response)
        time.sleep(50)
   

if __name__ == "__main__":
    poll()