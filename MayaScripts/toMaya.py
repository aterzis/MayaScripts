import sys, os, socket
from platform import system as myOs

def toMaya(filePath,selection):

    host='localhost'
    port=6001
    pythonOrMel="mel"
    extension=".mel"
    
    try:
        maya=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        maya.connect((host, port))
        
        #mel or python?
        if filePath.endswith("py"):
            pythonOrMel="python"
            extension=".py"
            
        if len(selection)>0:
            #save the selection in a file and source it. this seems to be the 
            #only simpleway that doesn't involve parsing
            homePath=""
            if myOs()=="Windows":
                homePath=os.path.join(os.environ.get("HOMEDRIVE"),os.environ.get("HOMEPATH"))
            elif myOs()=="Linux":
                homePath=os.environ.get("HOME")
            
            #create the file if it doesnt exist and write to it
            #fPath= (homePath + "/tmpSel" + extension).replace("\\","/")
            fPath= os.path.join(homePath,"tmpSel"+extension).replace("\\","/")
            f=open(fPath,"w")
            f.write(selection)
            f.close()
            
            #if it's mel, simply source the file
            #if python, do the imp.load_source trick
            if pythonOrMel=="mel":
                maya.send("source " + "\"" + fPath +"\"")
                print maya.recv(4000,0)
            else:
                #make sure the path exists
                if not os.path.isfile(fPath):
                    print (fPath + " is not a valid path.")
                    return
                maya.send("print " + selection)
                maya.send("python \"import imp\";")
                maya.send("python \"imp.load_source(\'tmpSel\',\'" + fPath +"\')\";")
                print maya.recv(4000,0)
            return
        
        elif len(filePath)>0: #file
            #if it's mel, simply source the file
            #if python, do the imp.load_source trick
            if pythonOrMel=="mel":
                maya.send("source " + "\"" + filePath.replace("\\","/") +"\"")
                print maya.recv(4000,0)
            else:
                bname=os.path.basename(filePath).split(".")[0]
                maya.send("python \"import imp\";")
                maya.send("python \"imp.load_source(\'" + bname + "\',\'" + filePath.replace("\\","/") +"\')\";")
                print maya.recv(4000,0)
            return
        maya.close()
    except:
        maya.close()
        
#get the args
filePath=sys.argv[1]
selection=sys.argv[2]

#gimme
toMaya(filePath,selection)