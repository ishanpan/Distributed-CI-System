import argparse
import os
import socket
import subprocess
import time


def poll ():
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--dispatcher-server",
    help="dispatcher host:port, " / "by default it uses localhost:8888",
    default="localhost:8888",
    action="store")

    parser.add_argument("repo",metavar="REPO",type=str,
    help="path to the repository this will observe")
    args = parser.parse_args()
    dispatcher_host, disptacher_port = args.dispatcher_server.split(":")

    while True:
        try:
            subprocess.check_output(["./update_repo.sh",args.repo])
        except subprocess.CalledProcessError as e:
            raise Exception("Could not update and check repo. " + "Reason : %s" % e.output)
                
        if os.path.isfile(".commit_id"):
                try:
                    response = helpers.communicate(dispatcher_host, 
                    int(disptacher_port),
                    "status")
                except socket.error as e:
                    raise Exception("Could not communicate with dispatcher server: %s" %e)

                if response == "OK":
                    commit = ""
                    with open(".commit_id","r") as f:
                        commit = f.readline()
                    response = helpers.communicate(dispatcher_host, int(disptacher_port), 
                    "dispatch:%s" %commit)

                    if response != "OK":
                        raise Exception("Could not dispatch the test: %s" %response)

                    print ("Dispatched!")
                
                else: 
                    raise Exception("Could not dispatch tests: %s" %response)
        time.sleep(5)
   

if __name__ == "__main__":
    poll()