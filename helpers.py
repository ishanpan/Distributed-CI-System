import socket
FORMAT  = 'utf-8'
def communicate(host, port, request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(request)
    response = s.recv(1024)
    s.close()
    return response