import requests

def getFreePort(url="http://127.0.0.1",startPort=3000,endPort=4000):

    port = startPort 
    free = False
    while not free:
        try:
            requests.get("%s:%d" % (url,port))
            port += 1
        except requests.exceptions.ConnectionError:
            free = True
        if port == endPort:
            port = -1
            break

    return port

if __name__ == "__main__":

    import sys

    port = getFreePort(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))

    print port