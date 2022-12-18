# boh

import socket
import time

HOST="192.168.1.16"
PORT=60000
user="admin"
password="normando"

cat_status_fname = "/usr/local/share/ad/cat_status.txt"
frequency_fname  = "/usr/local/share/ad/frequency.txt"

# intanto metto -5 che dovrebbe essere 'non collegato'
#t = open(frequency_fname, "w")
#t.write('-5')
#t.close()
#0 è cat ok


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))
    s.sendall(b"##CN;")
    data = s.recv(1024)
    if data.decode('utf-8') == '##CN1;':
        print("Connected")
        s.sendall(b"##ID00508adminnormando;")
        data = s.recv(1024)
        if data.decode('utf-8') == '##ID1;':
            print("Authenticated")

            s.sendall(b"AI0;")
            #data = s.recv(1024)
            #print(f"Received {data!r}")

            while True:
                s.sendall(b"FA;")
                data = s.recv(1024)
                #print(f"Received {data!r}")
                frequency = data.decode('utf-8')[2:].lstrip("0")[0:-3]+'00'
                print(frequency)
                t = open(frequency_fname, "w")
                t.write(frequency)
                t.close()
                time.sleep(1)

except socket.timeout:
    # qui
    print("ciao")
