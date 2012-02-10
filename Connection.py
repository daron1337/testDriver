import sys
import time
try:
    import requests
except:
    sys.exit("please install requests python package")

def waitUntilConnection(url, maxTries=None, interval=1, verbose=False):
    tries = 0
    success = False
    while not success:
        if maxTries and tries > maxTries:
            if verbose:
                print "Max tries reached. Connection unsuccessful."
            break
        if verbose:
            print "Trying to connect to url", url
        tries += 1
        try:
            requests.get(url)
        except:
            if verbose:
                print "Failed, trying again in %d seconds" % interval
            time.sleep(interval)
            continue
        if verbose:
            print "Success!"
        success = True

    return success

if __name__ == "__main__":

    success = waitUntilConnection("http://127.0.0.1:3000",maxTries=10,interval=1,verbose=True)
    print "Script finished with return value", success