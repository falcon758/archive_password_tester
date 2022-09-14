import pyzipper
import rarfile
import os
import sys	
from threading import Thread
import argparse
import signal
import time

parser = argparse.ArgumentParser(description='testPassword', epilog='Use the -h for help')
parser.add_argument('-i','--input', help='Insert the file path of compressed file', required=True)
parser.add_argument('-w','--wordlist', help='Insert the file path of wordlist file', required=True)

class Check:
    def __init__(self, arg):
        self.type = None
        self.wordlist = None

        if len(arg) == 0 or len(arg) < 4:
            parser.print_help()
            parser.exit()

        # Check File Exist
        if (self.CheckFileExist(arg)):
            self.getType(arg)
            self.wordlist = arg[3]
        else:
            print ('No such file or directory: ', arg[1])
            parser.exit()

    def CheckFileExist(self, arg):
        if (os.path.isfile(arg[1]) and os.path.isfile(arg[3])):
            return True
        else:
            return False
    
    def getType(self, arg):
        if os.path.splitext(arg[1])[1] == ".rar" or os.path.splitext(arg[1])[1]==".zip":
            self.type = os.path.splitext(arg[1])[1]
        else:
            print ('Extension Error')
            parser.exit()

class Handler:
    def __init__(self, typeCompress, wordlist):
        self.location = sys.argv[2]
        self.type = typeCompress
        self.wordlist = wordlist
        self.result = False
        self.killNow = False

        signal.signal(signal.SIGINT, self.exitGracefully)
        signal.signal(signal.SIGTERM, self.exitGracefully)

        self.GetFile()
        self.TryCrack()


    def exitGracefully(self, *args):
        self.killNow = True

    def GetFile(self):
        if self.type == '.zip':
            self.FileCrack = pyzipper.AESZipFile(self.location, 'r', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        else:
            self.FileCrack = rarfile.RarFile(self.location)

    def Brute(self, password):
        try:
            if self.type == '.zip':
                tryPass = password.encode()
            else:
                tryPass = password
            print (tryPass)
            self.FileCrack.extractall(pwd=tryPass)
            print ('Complete')
            print('Time:',time.process_time() - self.start_time,'s')
            print ('Password:',password)
            self.result = True
        except:
            pass

    def TryCrack(self):
        self.start_time = time.process_time()
        print ('Cracking...')
        self.SendRequest(self.wordlist)

    def SendRequest(self, passwordList):
        with open(passwordList) as wl:
            passwordList = wl.read().splitlines()
    
        for tryPass in passwordList:
            # Multi Thread:
            nThread = Thread(target=self.Brute, args=(tryPass, ))
            nThread.start()

            # Single Thread: 
            #self.Brute(tryPass)
            if self.result:
                return
            elif self.killNow:
            	 sys.exit()
def main():
    check = Check(sys.argv[1:])
    args = parser.parse_args()
    Handling = Handler(check.type, check.wordlist)
if __name__ == '__main__':
    main()
