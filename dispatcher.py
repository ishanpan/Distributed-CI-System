import argparse
from audioop import add
import os
import re
import socket
socket.socket
from socketserver import ThreadingMixIn, ThreadingTCPServer
import socketserver
import threading
import time

import helpers
FORMAT  = 'utf-8'

def dispatch_tests(server,commit_id):
    while True:
        print("Trying to dispatch to runners")
        for runner in server.runners:
            response = helpers.communicate((runner["host"]).encode(FORMAT),int(runner["port"]),("runtest:%s"%commit_id).encode(FORMAT))
            if response.decode(FORMAT) == "OK":
                print(f"adding id {commit_id}")
                server.dispatched_commits[commit_id] = runner
                if commit_id in server.pending_commits:
                    server.pending_commits.remove(commit_id)
                    return
                time.sleep(50)


class ThreadingTCPServer(socketserver.ThreadingMixIn,socketserver.TCPServer):
    runners = [] # Keeps track of test runner pool
    dead = False # Indicate to other threads that we are not running
    dispatched_commits = {} # Keeps track of commits dispatched
    pending_commits = [] # Keeps track of commits yet to be dispatched


class DispatcherHandler(socketserver.BaseRequestHandler):
    
    """
    The RequestHandler class for our dispatcher.
    This will dispatch test runners against the incoming commit
    and handle their requests and test results
    """

    command_re = re.compile(r"(\w+)(:.+)*")
    BUF_SIZE = 1024
    def handle(self):
        # Limit data size it receives
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(self.BUF_SIZE).strip().decode(FORMAT)
        command_groups = self.command_re.match(self.data)
        if not command_groups:
            self.request.sendall("Invalid Command".encode(FORMAT))
            return
        command = command_groups.group(1)

        if command == "status":
            print ("in status")
            self.request.sendall("OK".encode(FORMAT))
        elif command == "register":
            # Add this test runner to our pool
            print("Registering test runner")
            address = command_groups.group(2)
            print(address)
            host,port = re.findall(r':(\w*)', address)
            runner = {"host": host,"port": (port)}
            self.server.runners.append(runner)
            self.request.sendall("OK".encode(FORMAT))
        elif command == "dispatch":
            print ("going to dispatch")
            # parse commit id
            commit_id = command_groups.group(2)[1:]
            if not self.server.runners:
                self.request.sendall("No runners are registered".encode(FORMAT))
            else:
                self.request.sendall("OK".encode(FORMAT))
                #dispatch tests to one of the available runners
                dispatch_tests(self.server,commit_id)
        elif command == "results":
            print ("Got test results")
            results = command_groups.group(2)[1:]
            results = results.split(":")
            commit_id = results[0]
            length_msg = int(results[1])
            # 3 is the number of ":" in the sent command
            remaining_buffer = self.BUF_SIZE - (len(command) + len(commit_id) +len(results[1]) + 3)
            if length_msg > remaining_buffer:
                self.data += self.request.recv(length_msg - remaining_buffer).strip()
            del self.server.dispatched_commits[commit_id]
            if not os.path.exists("test_results"):
                os.makedirs("test_results")
            with open (f"test_results/{commit_id}","w") as f:
                data = self.data.split(":")[3:]
                data = "\n".join(data)
                f.write(data)
            self.request.sendall("OK".encode(FORMAT))
        else :
            self.request.sendall("Invalid command".encode(FORMAT))
    

def serve():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",help="dispatcher's host by default it uses localhost",
    default="localhost",action="store")
    parser.add_argument("--port",help="dispatcher's port, by default it uses 8888",
    default=8888,action="store")
    args = parser.parse_args()

     # Create the server
    server = ThreadingTCPServer((args.host, int(args.port)),DispatcherHandler)
    print(f'serving on {args.host} {args.port}')

    # Create a thread to check the runner pool
    def runnerpool_checker(server):
        def manage_commit_lists(runner):
            for commit, assigned_runner in server.dispatched_commits.items():
                if assigned_runner == runner:
                    del server.dispatched_commits[commit]
                    server.pending_commits.append(commit)
                    break
            server.runners.remove(runner)
        while not server.dead:
            time.sleep(50)
            for runner in server.runners:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    response = helpers.communicate((runner["host"]).encode(FORMAT),int(runner["port"]),("ping").encode(FORMAT))
                    if response.decode(FORMAT) != "pong":
                        print (f"removing runner {runner}")
                        manage_commit_lists(runner)

                except socket.error as e:
                    manage_commit_lists(runner)
        #redistribute the tests to any of the test runners
    def redistribute(server):
        while not server.dead:
            for commit in server.pending_commits:
                print ("Redistributing")
                print (server.pening_commits)
                dispatch_tests(server,commit)
                time.sleep(50)

    runner_heartbeat = threading.Thread(target=runnerpool_checker,args =(server,))
    redistributor = threading.Thread(target=redistribute,args=(server,))
    try:
        #start the following threads
        runner_heartbeat.start()
        redistributor.start()
        server.serve_forever()
    except (KeyboardInterrupt, Exception):
        # if any exception occurs, kill the thread
        server.dead = True
        runner_heartbeat.join()
        redistributor.join()


if __name__ == "__main__":
    serve()



