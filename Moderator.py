
from tkinter import *
import requests
import json
import os
import math
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import hashlib

fields = ('URL', 'Clients')


def integrity_check(file,hash):
	with open(file,'rb') as f:
		data = f.read()
	return hash == hashlib.sha256(data)


def accept_incoming_connections(start, end, url_of_file, file_name, output):
    client, client_address = SERVER.accept()
    output.insert(END, "%s:%s has connected." % client_address)
    addresses[client] = client_address
    data = json.dumps({"start": start, "end": end, "url": url_of_file, "filename": file_name})
    client.send(data.encode())
    chunk = client.recv(CHUNK_SIZE)
    if start == 0:
        with open(file_name, 'w+b') as f:
            f.write(chunk)
            chunk = client.recv(CHUNK_SIZE)
        f.close()

        with open(file_name, 'ab') as f:
            while chunk:
                f.write(chunk)
                chunk = client.recv(CHUNK_SIZE)
        f.close()

    else:
        with open(file_name, 'r+b') as f:
            f.seek(start)
            while chunk:
                f.write(chunk)
                chunk = client.recv(CHUNK_SIZE)

        f.close()


def threads(e, output):
    url_of_file = str(e['URL'].get())
    number_of_client = int(e['Clients'].get())
    file_name = url_of_file.split('/')[-1]
    i = 1
    while os.path.isfile(file_name):
        file_name = str(i)+file_name
        i += 1

    r = requests.head(url_of_file)
    file_size = int(r.headers['content-length'])
    output.insert(END, number_of_client)
    try:
        file_size = int(r.headers['content-length'])
    except:
        output.insert(END, "Invalid URL")
    part = math.floor(int(file_size) / number_of_client)
    threads = []
    for i in range(0, number_of_client):
        start = part * i
        end = start + part
        if i == number_of_client:
            end = file_size
        accept_thread = Thread(target=accept_incoming_connections,
                               kwargs={'start': start, 'end': end, 'url_of_file': url_of_file,
                                       'file_name': file_name, 'output': output}).start()
        threads.append(accept_thread)
    output.insert(END, "Waiting for Downloading...")
    j = 0
    for t in threads:
        t.join()
        j = j + 1
        if len(threads) == j:
            output.insert(END, "File Downloaded")
            SERVER.close()
    SERVER.close()


def makeform(root, fields):
    entries = {}
    for field in fields:
        row = Frame(root)
        lab = Label(row, width=22, text=field+": ", anchor='w')
        ent = Entry(row)
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT)
        ent.pack(side=RIGHT, expand=YES, fill=X)
        entries[field] = ent
    
    entries['URL'].insert(0, "http://mirrors.standaloneinstaller.com/video-sample/DLP_PART_2_768k.mp4")
    entries['Clients'].insert(0, "1")
    return entries


def GUI():
    win = Tk()

    topFrame = Frame(win)
    topFrame.pack()
    midFrame = Frame(win)
    midFrame.pack()
    bottFrame = Frame(win)
    bottFrame.pack()

    win.title("Moderator and Segmentation Unit")
    win.geometry("550x550+30+30")

    menu = Menu(win)
    win.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label='File', menu=filemenu)
    filemenu.add_command(label='New')
    filemenu.add_command(label='Open...')
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=win.quit)
    helpmenu = Menu(menu)
    menu.add_cascade(label='Help', menu=helpmenu)
    helpmenu.add_command(label='About')

    ents = makeform(topFrame, fields)

    scrollbar = Scrollbar(bottFrame)
    output = Listbox(bottFrame, height=15, width=50, yscrollcommand=scrollbar.set)
    output.pack(side=LEFT, fill=BOTH)
    scrollbar.pack(side=RIGHT, fill=Y)

    b1 = Button(midFrame, text='Go', command=(lambda e=ents: threads(e, output)))
    b1.pack(side=LEFT, padx=5, pady=5)
    b3 = Button(midFrame, text='Quit', command=win.quit)
    b3.pack(side=LEFT, padx=5, pady=5)
    win.bind('<Return>', (lambda event, e=ents: threads(e, output)))
    win.mainloop()


if __name__ == "__main__":
    HOST = ''
    PORT = 3300
    ADDR = (HOST, PORT)
    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)
    CHUNK_SIZE = 4096
    clients = {}
    addresses = {}
    SERVER.listen(5)
    GUI()
