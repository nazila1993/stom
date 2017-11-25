# -*- coding: UTF-8 -*-
#____________________________________________________________
# STOM - ver: 1.0
# 
# About:
# This programs is a service which receives SMS messages through
# some GSM dongles and at pre difined times send them to predifind
# mailing lists.
#
# Ehich dongle has its own TIME file and mailing list file.
# Also there is a logger system which has its own TIME file and
# mailing list file. 
# Log files are "Err.log" which collects ERRORs and "char.log" which
# collects unsupported characters to adding them in next versions.
#
# File hierarchy of this program is like this:
# 
# STOM
#  ├─ stop.py
#  ├─ conf.txt [id_1 : PORT]
#  ├─ log
#  .   ├─ char.log
#  .   ├─ Err.log
#  .   ├─ time.txt
#  .   └─ list.txt
#  ├─ id_1
#  .   ├─ time.txt
#  .   └─ list.txt
#  ├─ id_2
#  .   .
#  .   .
#  .   .
#
# Contact me on sotothe@gmail.com

#____________________________________________________________
# Constants

INIT_PATH  = "C:\\Users\\SoToThe\\Documents\\Works\\text2mail"
EMAIL_ADDR = "textmsg2email@gmail.com"
EMAIL_PASS = "73*7m59z3m4i1"
BAUD_RATE  = 921600
SMTP_PORT  = 587
VERBOSE_M  = True

#____________________________________________________________
# Imports

from datetime import datetime
import os
import time
import smtplib
import serial
import re
import codecs

#____________________________________________________________
# SIM class

class Sim(object):
    sim_id = ""
    port = ""
    m_list = []
    m_times = []
    
    def __init__(self, sim_id, port, m_list, m_times):
        self.sim_id = sim_id
        self.port = port
        self.m_list = m_list
        self.m_times = m_times
        
#____________________________________________________________
# GSM class

class Gsm(object):
    def __init__(self, port):
        self.connect(port)

    def connect(self, port):
        self.ser = serial.Serial(port, BAUD_RATE, timeout=5)
        self.send_command(b'ATZ\r')
        self.send_command(b'AT+CMGF=1\r')
        
    def send_command(self, command, getline=True):
        self.ser.write(command)
        data = ''
        if getline:
            data=self.read_line()
        return data 

    def read_line(self):
        data = self.ser.readline()
        return data 

    def get_all_sms(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        command = b'AT+CMGL="all"\r'    ### To get all messages both read and unread ###
        self.send_command(command,getline=False)
        self.ser.timeout = 2
        data = self.ser.readall()
        return data
        
    def send_sms(self, msg, recipient):
        self.ser.write(b'AT+CMGS="' + recipient.encode() + b'"\r')
        time.sleep(0.5)
        self.ser.write(msg.encode() + b"\r")
        time.sleep(0.5)
        self.ser.write(bytes([26]))
        time.sleep(0.5)
        
    def clear_sms(self):
        self.ser.write(b'AT+CMGD=1,4\r')
        return True
        
    def close(self):
        self.ser.close()     

#____________________________________________________________
# Urdu char map

def char_map(x):
    ch_map = {
        '060C' : '،',
        '061B' : '؛',
        '061F' : '؟',
        '0620' : 'ؠ',
        '0621' : 'ء',
        '0622' : 'آ',
        '0623' : 'أ',
        '0624' : 'ؤ',
        '0625' : 'إ',
        '0626' : 'ئ',
        '0627' : 'ا',
        '0628' : 'ب',
        '0629' : 'ة',
        '062A' : 'ت',
        '062B' : 'ث',
        '062C' : 'ج',
        '062D' : 'ح',
        '062E' : 'خ',
        '062F' : 'د',
        '0630' : 'ذ',
        '0631' : 'ر',
        '0632' : 'ز',
        '0633' : 'س',
        '0634' : 'ش',
        '0635' : 'ص',
        '0636' : 'ض',
        '0637' : 'ط',
        '0638' : 'ظ',
        '0639' : 'ع',
        '063A' : 'غ',
        '063E' : 'ؾ',
        '063F' : 'ؿ',
        '0640' : 'ـ',
        '0641' : 'ف',
        '0642' : 'ق',
        '0643' : 'ك',
        '0644' : 'ل',
        '0645' : 'م',
        '0646' : 'ن',
        '0647' : 'ه',
        '0648' : 'و',
        '0649' : 'ى',
        '064A' : 'ي',
        '0660' : '٠',
        '0661' : '١',
        '0662' : '٢',
        '0663' : '٣',
        '0664' : '٤',
        '0665' : '٥',
        '0666' : '٦',
        '0667' : '٧',
        '0668' : '٨',
        '0669' : '٩',
        '066A' : '٪',
        '066B' : '٫',
        '066C' : '٬',
        '066D' : '٭',
        '0672' : 'ٲ',
        '0673' : 'ٳ',
        '067E' : 'پ',
        '0686' : 'چ',
        '0698' : 'ژ',
        '06A9' : 'ک',
        '06AF' : 'گ',
        '06BE' : 'ھ',
        '06C1' : 'ہ',
        '06CC' : 'ی',
        '06D2' : 'ے',
        '06D4' : '۔',
        '06D5' : 'ە',
        '06F0' : '۰',
        '06F1' : '۱',
        '06F2' : '۲',
        '06F3' : '۳',
        '06F4' : '۴',
        '06F5' : '۵',
        '06F6' : '۶',
        '06F7' : '۷',
        '06F8' : '۸',
        '06F9' : '۹'}
    try:
        return ch_map[x]
    except:
        x = x + '\r\n'
        text_writer(x, 'x')
        return '?'

#____________________________________________________________
# Error List
# This is a list of ERRORs
# This function get an ERROR CODE and returns ERROR DESCRIPTION.
        
def err_code(x):
    return {
        1 : "File does't exist: ",
        2 : "Unable to open file: ",
        3 : "There is no defined SIM in 'conf.txt'.",
        4 : "There is no defined sending time for SIM number: ",
        5 : "Unable to connect to Gmail.",
        6 : "Unable to write to file: ",
        7 : "Unable to connect to GSM: ",
        8 : "There is no defined email_address for SIM number: ",
        9 : "There is no defined email_address for sending logs.",
        10: "There is no defined sending time for sending logs."
    }[x]

#____________________________________________________________
# Error Logger
# This function gets an ERROR Code and extra information (if needed)
# and writes an ERROR log in the Err.log file.

def err_logger(code, tail = ""):
    err = datetime.now().strftime("%Y/%m/%d - %H:%M") + " > " + err_code(code) + tail + "\r\n"
    text_writer(err, 'E')
        
#____________________________________________________________
# File Reader
# This function is a specialized File reader for CONF, TIME and LIST files.

def read(sim_id, tail = ""):
    content = []
    if sim_id == 'c':
        tail_path = "\\" + tail + ".txt" 
    else:
        tail_path = "\\" + sim_id + "\\" + tail + ".txt"
        
    path = INIT_PATH + tail_path
    
    if os.path.exists(path):
        if VERBOSE_M: print('Reading file: ', path)# Verbose mode

        for line in open(path, encoding='utf-8'):
            try:
                li = line.strip()
                if not li.startswith('#'):
                    content.append(line.rstrip())
            except:
                err_logger(2, path)
    else:
        err_logger(1, path)
    
    return content

#____________________________________________________________
# Logger Initializer
# This Function initializing the Logger and reads it's Time and List files.

def logger_init():
    if VERBOSE_M: print('Initializing the logger...')# Verbose mode
        
    sim_id = 'log'
    port = 'None'
    
    m_list = read(sim_id, 'list')
    
    if len(m_list) == 0:
        if VERBOSE_M: print('Logger mailng list is empty!')# Verbose mode
        err_logger(9)
        
    m_times = read(sim_id, 'time')
    
    if len(m_times) == 0:
        if VERBOSE_M: print('Logger sending times is empty!')# Verbose mode
        err_logger(10)
        
    sims.append(Sim(sim_id, port, m_list, m_times))

#____________________________________________________________
# Initializer
# This function reads CONF, TIME and LIST files and initializing the program.

def init():
    if VERBOSE_M: print('Reading configurations and initializing the program...')# Verbose mode

    logger_init()
    content = read('c','conf')
    for sim in content:
        sim = sim.split(':')
        
        sim_id = sim[0].strip()
        
        port = sim[1].strip()
        
        m_list = read(sim_id, 'list')
        if len(m_list) == 0:
            err_logger(8,sim_id)
            
        m_times = read(sim_id, 'time')
        if len(m_times) == 0:
            err_logger(4,sim_id)

        sims.append(Sim(sim_id, port, m_list, m_times))
    if len(sims) == 1:
        err_logger(3)
    return sims

#____________________________________________________________
# Time Dictionary
#This Function makes a dictionary of the predifined times.

def time_dic(sims):
    if VERBOSE_M: print('Collecting all sending times...')# Verbose mode

    dic = {}
    for x in sims:
        for y in x.m_times:
            dic[y] = x.sim_id
    if VERBOSE_M: print('Collecting all sending times is done!')# Verbose mode

    return dic

#____________________________________________________________
# Find Sim
#This Function gets an ID and returns the SIM object.

def find_sim(i):
    for s in sims:
        if s.sim_id == i:
            return s
        
#____________________________________________________________
# Send mail
# This function gets a message and its recipient(s) and the subject,
# then send the message to recipient(s) as an email.

def send_mail(msg, recipient, subj=""):
    if not subj == "":
        subj = subj + ", "
    
    fail = 0
    subj = subj + datetime.now().strftime("%Y/%m/%d - %H:%M")
    msg = 'Subject: {}\n\n{}'.format(subj, msg)
    msg = msg.encode('utf-8')
        
    while fail < 3:
        try:
            if VERBOSE_M: print('Sending email....') # Verbose mode

            server = smtplib.SMTP('smtp.gmail.com', SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDR, EMAIL_PASS)
            server.sendmail(EMAIL_ADDR, recipient, msg)
            server.quit()
            if VERBOSE_M: print('Done!')
            return True
        
        except:
            if VERBOSE_M: print('Sending failed! attempn No = ', fail) # Verbose mode
            
            fail += 1
            time.sleep(300)
    
    err_logger(5)
    return False

#____________________________________________________________
# Text writer
# This function writes string to files.

def text_writer(txt, tail):        
    if tail == 'E':
        tail_path = "\\log\\" + "Err.log"
    elif tail == 'x':
        tail_path = "\\log\\" + "char.log"
    else:
        tail_path = "\\sms\\" + tail + ".txt"

    path = INIT_PATH + tail_path
    if VERBOSE_M: print('Writing text to file: ...', tail_path)# Verbose mode
    
    if os.path.exists(path):
        with open(path, 'ab') as txt_file:
            try:
                txt_file.write(txt.encode('UTF-8'))

            except:
                err_logger(6, path)
    else:
        with open(path, 'wb') as txt_file:
            txt_file.write(txt.encode('UTF-8'))
            
#____________________________________________________________
# Message Extractor   
# This function extracts message text from a string
    
def extract(msg):
    msg = msg.split('"')
    del msg[0]
    msg = str(msg)
    msg = re.sub(r"(\[)?['\"](\\)+r(\\)+n", "", msg)
    msg = re.sub(r"((\\)+r(\\)+n)+(OK)|((\\)+r(\\)+n)?['\"]?(\])?", "", msg)
    return msg
    
#____________________________________________________________
# Decode
# This function decodes a BYTE STREAM to a character list

def decode(string):
    if VERBOSE_M: print('Decoding SMS messages...')# Verbose mode
        
    if re.match(r"0[\d,A-F]{3}", string):
        words = hex_to_word(string)
        for i, word in enumerate(words):
            words[i] = char(word)
        string = ''.join(words)
        return string
    elif re.match(r"\\\\n", string):
        return '\r\n'
    else:
        return string

#____________________________________________________________
# Hex_to_word
# This function converts a BYTE STREAM to a list of WORDs

def hex_to_word(string):
    counter = 0
    word = ""
    word_list = []
    while counter < len(string):
        word += string[counter]
        counter += 1
        if counter % 4 == 0:
            word_list.append(word)
            word = ""
            continue
    return word_list

#____________________________________________________________
# Char
# This function converts a WORD (32 bits) to a character

def char(word):
    if re.match(r"0[1-9][\d,A-F]{2}", word):
        return char_map(word)
    else:
        try:
            ch = str(codecs.decode(re.sub(r'(0){2}','',word), 'hex'),'ascii')
        except:
            ch = '"' # This is an alternative for the characters « , »
        return ch
    
#____________________________________________________________
# SMS Normalizer
# This function get the SMS messages in raw format which contains lots of extra characters,
# and returns it back as a neat text.

def normalizer(txt):
    if VERBOSE_M: print('Normalizing SMS messages...')# Verbose mode
        
    out = ""
    txt = txt.split('+CMGL:')
    del txt[0]
    for sms in txt:
        sms = sms.replace('","','";"')
        sms = sms.split('";"')
        del sms[2]; del sms[0]
        out += sms[0] + ":\r\n" + decode(extract(sms[1])) + "\r\n..............................\r\n"
        
    if VERBOSE_M: print('Normalizing SMS messages is done!')# Verbose mode
    return out
    
#____________________________________________________________
# SMS To Text
# This function reads SMS messages from GMS and write them into the specified text file.

def sms_to_text(sid):
    if VERBOSE_M: print('Reading SMS messages...')# Verbose mode
        
    try:
        a= gsm = Gsm(find_sim(sid).port)
        b= txt = gsm.get_all_sms()
        gsm.close()
        if VERBOSE_M: print('Reading SMS messages id done!')# Verbose mode
            
    except:
        err_logger(7, sid)
        if VERBOSE_M: print('Unable to connect to GMS module: ', sid)# Verbose mode
        return False
    
    txt = normalizer(str(txt))
    text_writer(txt, sid)
    return True
    
#____________________________________________________________
# SMS Sender
# This function IS NOT BEEN USED.

def sms_sender(sid, msg, recipient):
    if VERBOSE_M: print('Sending a SMS message...')# Verbose mode
        
    try:
        gsm = Gsm(find_sim(sid).port)
        gsm.send_sms(msg, recipient)
        gsm.close()
        if VERBOSE_M: print('Sending a SMS messageid done!')# Verbose mode

    except:
        err_logger(7, sid)
    
#____________________________________________________________
# SMS Clear
# This function removes SMS messages from a SIM or GSM permanently.

def sms_clear(sid):
    if VERBOSE_M: print('Clearing SMS messages...')# Verbose mode
    try:
        gsm = Gsm(find_sim(sid).port)
        gsm.clear_sms()
        gsm.close()
        if VERBOSE_M: print('Clearing SMS messages is done!')# Verbose mode
            
    except:
        err_logger(7, sid)

#____________________________________________________________
# Text Clear
# This function makes a text file empty.

def txt_clear(path):
    open(path, 'w').close()

#____________________________________________________________
# Pre send

def pre_send(sid, path, subj = ""):
    if VERBOSE_M: print('Pre sending...')# Verbose mode
        
    if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as text:
                    data = text.read()
                    if data == '':
                        data = 'There is nothing new!'
                if send_mail(data, find_sim(sid).m_list, subj):
                    txt_clear(path)
            except:
                err_logger(2, path)
    else:
        err_logger(1, path)
    
#____________________________________________________________
# Go
# When it's time to do something this function goes to do it.

def go(sid):
    if VERBOSE_M: print('Go ',sid,':')# Verbose mode
        
    if sid == 'log':
        path = INIT_PATH + "\\log\\" + "Err.log"
        pre_send(sid, path, 'Err_log')
        path = INIT_PATH + "\\log\\" + "Char.log"
        pre_send(sid, path, 'Unsupported characters')
    else:
        path = INIT_PATH + "\\sms\\" + sid + ".txt"
        if sms_to_text(sid):
            sms_clear(sid)
            pre_send(sid, path)
        else:
            txt_clear(path)

#____________________________________________________________
# Start
# This function defines necessary variables, calls the initializer,
# and starts checking time incase it is time to do something.

def start():    
    dic = time_dic(sims)
    last_time = ''
    if VERBOSE_M: print('Waiting for the first time...')# Verbose mode    

    while True:
        now = datetime.now().time().strftime("%H:%M")
        if not last_time == now:
            last_time = now
            if now in dic.keys():
                go(dic[now])
        time.sleep(20)

#____________________________________________________________
# Start of the program

if VERBOSE_M: print('Program starts...')# Verbose mode
sims = []
sims = init()

start()
#go('1') #This line is for testing!