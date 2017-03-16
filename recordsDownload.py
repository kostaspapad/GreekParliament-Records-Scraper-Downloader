import sys,getopt
import time
import sqlite3
import urllib2
import requests
import datetime


def getAllDocFiles(fromID = 0):

    # Connect to sqlite
    try:
        conn = sqlite3.connect('voulidatabase.db')
        #print "--:connected to database"

        cursor = conn.execute("SELECT Date, DocumentLocation, DocumentName FROM vouliData WHERE (Not DocumentName LIKE '%No doc%') and ID > ?", [fromID])                
        
        # Iterate on results
        for row in cursor:

           # Look for rows containing (morning conference identifier), insert extension doc or docx
           if len(row[0]) > 10:
               new_file_name = datetime.datetime.strptime(row[0][:10], "%d/%m/%Y").strftime("%d-%m-%Y") + "Morning." + row[2].split('.')[1] 
               
           else:
               # Change date format and use it as file_name
               new_file_name = datetime.datetime.strptime(row[0], "%d/%m/%Y").strftime("%d-%m-%Y") + '.' + row[2].split('.')[1]
          
           # Call download function
           download(row[1] + '/' + row[2], new_file_name)
           
           # Delay for next download
           time.sleep(2)
           
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if conn:
            conn.close()

def download(file_loc, new_file_name):
    url = 'http://www.hellenicparliament.gr/' + file_loc
    
    print "Downloading:" + new_file_name
    
    try:
        dl = requests.get(url, stream=True)
    
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print e
        sys.exit(1)
    
    with open(new_file_name, 'wb') as f:
        for chunk in dl.iter_content(1024 * 1024 * 2):  # 2 MB chunks
            f.write(chunk)

def main(argv):

   try:
        opts, args = getopt.getopt(argv,"hd:f:a")
   except getopt.GetoptError:
        usage()
        sys.exit(2)

   for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

        elif opt in ("-d", "--download"):
            print 'Single doc download'
            link = arg.split('/')
            download('/' + link[1] + '/' + link[2], link[3])
            
        elif opt in ("-f", "--fromID"):
            print "Start from id"
            start_time = time.time()
            getAllDocFiles(int(arg))
            print("--- %s seconds ---" % (time.time() - start_time))
            
        elif opt in ("-a", "--all"):
            print "Download all files"
            start_time = time.time()
            getAllDocFiles()
            print("--- %s seconds ---" % (time.time() - start_time))

        else:
            assert False, "unhandled option"

def usage():
    usage = """-----------------------------------
    Vouli file downloader v0.1
    Dependencies:
        Requests,
        sqlite3

    -h --help                                        Print this
    -d --download <locationLink+documentName>        Download single doc file e.x -d '/UserFiles/32323-2312382-232852-2929/es2828582.doc'
    -f --fromID                                      Download single file specified by ID in database
    -a --all                                         Download all doc files
    -----------------------------------
    """
    print usage

if __name__ == "__main__":
   main(sys.argv[1:])
