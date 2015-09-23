import time
import sys
import socket
import os
import threading
from random import randint
from datetime import datetime

is_coord = 0
coord = 0
DIR = '/tmp/bully/'
host = ''
port = int(sys.argv[1])
while_election = False


def check_coord_exists(p):
    global coord
    ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns.settimeout(10)
    try:
        ns.connect((host, int(p)))
        ns.send('Voce e o coordenador?'.encode())
        data = ns.recv(2048)
        ans = data.decode('utf-8')
        if ans == 'YES':
            coord = int(p)
        ns.close()
    except:
        print('Nao conseguiu conectar ao processo')


def check_coord_awake():
    global while_election
    while True:
        time.sleep(randint(5,15))
        if coord != 0 and is_coord == 0 and while_election == False:
            ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ns.settimeout(10)
            try:
                ns.connect((host, coord))
                ns.send('AYA'.encode())
                print('AYA')
                print(datetime.now())
                data = ns.recv(2048)
                msg = data.decode('utf-8')
                verify_msg(None,None,msg=msg)
                ns.close()
            except socket.error as e:
                print('Nao encontrou o coordenador, iniciando nova eleicao...')
                while_election = True
                new_election()

            
def new_election():
    global port
    global while_election
    global DIR
    global is_coord
    plist = os.listdir(DIR)
    candidates=[]
    for p in plist:
        if int(p) > port:
            candidates.append(int(p))
    won_election = True
    
    for c in candidates:
        ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            ns.connect((host, c))
            ns.send('ELECTION'.encode())
            data = ns.recv(2048)
            msg = data.decode('utf-8')
            if msg == 'OK':
                print('OK received')
                won_election = False
            ns.close()
        except socket.error as e:
            print('Falha em comunicar eleicao')
            
    if won_election == True:
        is_coord = 1
        coord = port
        while_election = False
        i_won()
        
        
def i_won():
    global port
    global while_election
    global DIR
    print('Sou o Coordenador')
    plist = os.listdir(DIR)
    candidates=[]
    for p in plist:
        if int(p) != port:
            ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                ns.connect((host, int(p)))
                ns.send('COORDINATOR {}'.format(port).encode())
                ns.close()
            except socket.error as e:
                print('Falha em enviar COORDINATOR')


def answer_socket(conn, addr):
    data = conn.recv(2048)
    msg = data.decode('utf-8')
    verify_msg(conn, addr, msg)
                           
    
def verify_msg(conn, addr, msg):
    global while_election
    global is_coord
    global coord
    global while_election
    if msg == 'AYA':
        if is_coord == 1:
            print('IAA')
            conn.send('IAA'.encode())
    elif msg == 'IAA':
        print('Coordinator is alive')
    elif msg == 'Voce e o coordenador?':
        if is_coord == 1:
            conn.send('YES'.encode())
        else:
            conn.send('NO'.encode())
    elif msg == 'ELECTION':
        conn.send('OK'.encode())
        if while_election == False:
                while_election = True
                new_election()
    elif 'COORDINATOR' in msg:
        print(msg)
        msplit=msg.split()
        is_coord = 0
        coord = int(msplit[1])
        while_election = False
    else:
        pass


def main():
    global is_coord
    global DIR
    global port
    global coord
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((host, port))
        except socket.error as e:
            print(str(e))

        try:
            os.chdir(DIR)
        except:
            os.mkdir(DIR)

        plist = os.listdir(DIR)

        if not plist:
            is_coord = 1
            coord = port
            print('Sou o coordenador')

        mySock = sys.argv[1]
        f = open(mySock, 'w+')

        if is_coord == 0:
            for p in plist:
                try:
                    check_coord_exists(p)
                except:
                    print('connection failed')
        s.listen(5)

        thread_check_coord = threading.Thread(target=check_coord_awake, args=())
        thread_check_coord.daemon = True
        thread_check_coord.start()

        if is_coord == 0:
            print('O Coordenador e: {}'.format(coord))
        while True:
            conn, addr = s.accept()
            new_thread = threading.Thread(target=answer_socket, args=(conn, addr))
            new_thread.daemon = True
            new_thread.start()

    except KeyboardInterrupt:
        os.remove(sys.argv[1])
        sys.exit()

    except:
        print('Remove File')
        os.remove(sys.argv[1])
        

if __name__ == "__main__":
    main()