from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from tkinter import *
import math
import json
import requests

fields = ('Host', 'Port')


def Handler(start, end, url, filename, startServer, output):
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    reqfile = requests.get(url, headers=headers, stream=True)
    if reqfile.status_code == 206:
        with open(filename, 'r+b') as f:
            seek = int(start-startServer)
            f.seek(seek)
            f.write(reqfile.content)
    else:
        output.insert(END, "Download in parts not Supported")


def threads(e, output):
    addr = (e['Host'].get(), int(e['Port'].get()))

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(addr)

    data = client_socket.recv(CHUNK_SIZE)
    data = json.loads(data.decode())
    startServer = data.get("start")
    endServer = data.get("end")
    url_of_file = data.get("url")
    file_name = data.get("filename")
    file_size = int(endServer)-int(startServer)
    output.insert(END, str(round(file_size/(1024*1024), 3))+"MB")
    fp = open(file_name, "wb")
    fp.write(('\0' * file_size).encode())
    fp.close()


    number_of_threads = 4
    threads = []
    part = math.floor(file_size / number_of_threads)
    start = startServer
    end = start + part
    for i in range(number_of_threads):
        t = Thread(target=Handler, kwargs={'start': start,
                                           'end': end, 'url': url_of_file, 'filename': file_name,
                                           'startServer': startServer, 'output': output})
        t.setDaemon(True)
        t.start()
        threads.append(t)
        start = start + part
        end = start + part
        if i == number_of_threads-2:
            end = endServer
    i = 0
    for t in threads:
        t.join()
        i = i + 1
        if len(threads) == i:
            break


    output.insert(END, '%s downloaded' % file_name)
    output.insert(END, 'Sending file segment to moderator.')
    with open(file_name, 'rb') as f:
        data = f.read(CHUNK_SIZE)
        while data:
            client_socket.send(data)
            data = f.read(CHUNK_SIZE)
    output.insert(END, "File segment sent to moderator.")
    client_socket.close()


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
    entries['Host'].insert(0, "127.0.0.1")
    entries['Port'].insert(0, "3300")
    return entries


def GUI():
    win = Tk()

    topFrame = Frame(win)
    topFrame.pack()
    midFrame = Frame(win)
    midFrame.pack()
    bottFrame = Frame(win)
    bottFrame.pack()

    win.title("Peer")
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
    
    CHUNK_SIZE = 4096
    GUI()
