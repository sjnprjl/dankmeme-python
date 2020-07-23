#!/usr/bin/env python
from config import *
from fbchat import log , Client
from fbchat.models import *
import wget
import os
import datetime
import subprocess
from bs4 import BeautifulSoup as bs
import requests
import time
import random
b_begin = "?!"
bot_name = "<bot>"

lower = lambda s: s[:1].lower() + s[1:] if s else ''

def fortune(stream):
    it = iter(stream)
    result = next(it)
    for n,item in enumerate(it):
        if random.randint(0,n+1) == 0:
            result = item
    return result

class DankMeme(Client):
    '''DankMeme created just for fun!'''
    def show_help(self):
        return '''<bot>:
       Usage: {begin}command [mention]
        --------------
        Command(s):
            -  scold
            -  roast    
            -  meme
        Example(s):
            {begin}scold @friend_name [default: 'me']
            {begin}roast @friend_name [default: 'me']
            {begin}meme
        '''.format(begin=b_begin)
    def show_error(self, error):
        return error + '\n' + self.show_help()

    def scold(self , pid , thread_id , thread_type):
        user = self.fetchUserInfo(pid)[pid] 
        x = datetime.datetime.now()
        m = x.strftime("%M")
        ml = x.strftime("%f")
        s = x.strftime("%S")
        to_bitch = str(user.uid) + str(ml) + str(m) + str(s) + ".jpg"
        wget.download(user.photo , to_bitch)
        time.sleep(5)
        subprocess.call("composite -geometry +130+80 {} {} {}".format(to_bitch , "meme_profile/darlagyo_crop.jpg" , to_bitch) , shell=True)
        subprocess.call("convert {} -fill blue -gravity North -pointsize 20 -annotate +0+20 'Dar lagyo my lord!' {}".format(to_bitch , to_bitch) , shell=True)
        self.sendLocalImage(
            to_bitch, 
            thread_id=thread_id,
            thread_type=thread_type,
         )
        os.remove(to_bitch)

    def roast(self , pid , thread_id , thread_type):
        user = self.fetchUserInfo(pid)[pid]
        with open('roasts.txt') as f:
            rst = fortune(f)
        text = "@{}, {}".format(user.name , lower(rst))
        time.sleep(5)
        self.send(Message(  text = bot_name + ": " + text , 
                            mentions = [  Mention(thread_id = pid ,
                                          offset = len(bot_name) + 2 ,
                                          length = len(user.name) + 1 ) ]) , 
                            thread_id = thread_id ,
                            thread_type = thread_type  )

    def send_random_meme(self , thread_id , thread_type):
        random_number = random.choice( range(1,10) )
        url = "https://www.memedroid.com/memes/top/day/" + str(random_number)

        r = requests.get(url)
        site = bs(r.text , 'lxml')
        memes = site.findAll('img' , {"class" : "img-responsive"})

        parsed_memes = []
        for meme in memes:
            src = meme['src']
            if "http" in src:
                parsed_memes.append(src)

        self.sendRemoteImage(
            random.choice(parsed_memes), 
            thread_id=thread_id,
            thread_type=thread_type,
         )

    def send_text_message(self , message , thread_id , thread_type):
        time.sleep(5)
        self.send(  Message(text = bot_name + ": " + message) ,
                    thread_id = thread_id ,
                    thread_type = thread_type  )

    def meme_activate(self , message_object , author_id , thread_id , thread_type):
        user_commands = message_object.text.split(" ")
        bot_begin = user_commands[0][:2]
        bot_command = user_commands[0][2:]
        try:
            mention = message_object.mentions[0]
        except:
            mention = ""
        try:
            bot_mention = user_commands[1]
        except IndexError:
            bot_mention = ""
        if bot_begin == b_begin:
            if bot_command == "help":
                self.send_text_message(  self.show_help() ,
                                    thread_id ,
                                    thread_type  )
            elif bot_command == "meme":
               self.send_random_meme(thread_id , thread_type)
            elif bot_command == "roast" and len(bot_mention) > 0:
               if bot_mention == "me":
                   self.roast(self.uid , thread_id , thread_type)
               else:
                   if mention == "":
                       self.send_text_message(
                               self.show_error("Error: '{}' is not available in this group".format(bot_mention)),
                               thread_id = thread_id ,
                               thread_type = thread_type  )
                   else:
                       self.roast(mention.thread_id , thread_id , thread_type)
            elif bot_command == "scold" and len(bot_mention) > 0:
               if bot_mention == "me":
                   self.scold(self.uid , thread_id , thread_type)
               else:
                   if mention == "":
                       self.send_text_message(
                               self.show_error("Error: '{}' is not available in this group".format(bot_mention)),
                               thread_id = thread_id ,
                               thread_type = thread_type  )
                   else:
                       self.scold(mention.thread_id , thread_id , thread_type)
            else:
                 self.send_text_message(
                         self.show_error("Error: '{command}' command is not recognized!".format(command=bot_command)),
                         thread_id = thread_id,
                         thread_type = thread_type  )

    def onMessage(self, message_object, author_id, thread_id, thread_type, **kwargs):
        if thread_type == ThreadType.GROUP:
            self.meme_activate(message_object , author_id , thread_id , thread_type)

if __name__ == "__main__":
    DankMeme(USERNAME , PASSWORD).listen()
