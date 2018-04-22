'''
Functions such as getting models list, details for livestreamer, etc.
'''
from config import *
from bs4 import BeautifulSoup
import re
import time
import datetime
import signal
import os


def Models_list(client):
    # Moving to followed models page
    try:
        logging.info("Redirecting to " + URL_follwed)
        r2 = client.get(URL_follwed)
    except Exception as e:
        logging.error('Some error during connecting to ' + URL)
        logging.error(e)
        return []
    soup = BeautifulSoup(r2.text, "html.parser")
    # print('Page Source for ' + URL_follwed + '\n' + r2.text)

    page_source = 'Page Source for ' + URL_follwed + '\n' + r2.text
    if Debugging == True:
        Store_Debug(page_source, "modellist.log")
    ul_list = soup.find('ul', class_="list")
    li_list = soup.findAll('li', class_="cams")
    # logging.debug(li_list)
    if Debugging == True:
        Store_Debug(li_list, "li_list.log")
    # Finding who is not offline
    online_models = []
    for n in li_list:
        if n.text != "offline":
            if n.parent.parent.parent.div.text == "IN PRIVATE":
                logging.warning(n.parent.parent.a.text[1:] + ' model is now in private mode')
            else:
                online_models.append(n.parent.parent.a.text[1:])
    logging.info('[Models_list] %s models are online: %s' % (len(online_models), str(online_models)))
    return online_models


def Select_models(Models_list):
    # Select models that we need
    Wish_list = Wishlist()
    Model_list_approved = []
    logging.info('[Select_models] Which models are approved?')
    for model in Models_list:
        if Disable_wishlist == False:
            if model in Wish_list:
                logging.info("[Select_models] " + model + ' is approved')
                Model_list_approved.append(model)
        else:
            logging.info("[Select_models] " + model + ' is approved')
            Model_list_approved.append(model)
    if len(Model_list_approved) == 0:
        logging.warning('[Select_models]  No models for approving')
    return Model_list_approved


def Password_hash(string):
    # replace special chars for unix shell! \$ and \/ and \= mostly
    string = string.replace("\u003D", "\=")
    string = string.replace("$", "\$")
    string = string.replace("/", "\/")
    return string


def Get_links(client, Models_list_store):
        # Get the models options for creating rtmpdump string
    if (len(Models_list_store) != 0):
        for model in Models_list_store:
            # write models livestreamer string to file
            flinks = open(Script_folder + '/' + model + '.sh', 'w')
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')

            form_dict = {
                "model_name": model,
                "video_folder": Video_folder,
                "converted_folder": Converted_folder,
                "date_string": st,
            }
            script = """#!/bin/sh
streamlink --force --quiet --output "%(video_folder)s/Chaturbate_%(model_name)s_%(date_string)s.flv" http://chaturbate.com/%(model_name)s best
if ffmpeg -loglevel quiet -i "%(video_folder)s/Chaturbate_%(model_name)s_%(date_string)s.flv" -vcodec copy -acodec libmp3lame "%(converted_folder)s/Chaturbate_%(model_name)s_%(date_string)s.flv.mp4"; then
    rm "%(video_folder)s/Chaturbate_%(model_name)s_%(date_string)s.flv"
fi;
""" % form_dict
            flinks.write(script)
            flinks.close()
            os.chmod(Script_folder + '/' + model + '.sh', 0o777)
            logging.info('[Get_links] ' + model + '.sh is created')
    else:
        logging.warning('[Get_links] No models to get!')


def Rtmpdump_models():
    models = []
    for line in os.popen("ps xa | grep streamlink | grep -v 'grep'"):
        fields = line.split()
        # EXAMPLE: ['65192', 'pts/7', 'Sl+', '0:01', '/usr/bin/python',
        # '/usr/local/bin/livestreamer', '--output',
        # 'Video_folder_date.timestamp_username.flv',
        # 'http://chaturbate.com/username', 'best', '--quiet']

        # 28908 pts/4    R+     0:00 /home/tom/Projects/CaptureBate/virtualenv/bin/python2.7
        # /home/tom/Projects/CaptureBate/virtualenv/bin/livestreamer --force --quiet --output
        # /home/tom/Projects/CaptureBate/Captured/Chaturbate_2016.31.08_22.04_sexydevilxx.flv
        # http://chaturbate.com/sexydevilxx best

        try:
            pid = fields[0]
            process = fields[5]
        except IndexError as e:
            print (fields)
            print (e)
            continue

        if "streamlink" in process:
            if Video_folder in fields[9]:
                if "http://chaturbate.com/" in (fields[10]):
                    models.append(fields[10][22:])
            else:
                logging.debug('Not In Video Folder: \n' + fields)
    logging.debug('Streamlink shows the following models: \n' + str(models))
    return models


def Compare_lists(ml, mlr):
    # Comparing old models list(Main list) to new(updated) models list
    # This loop is used for removing offline models from main list
    ml_new = []
    logging.info('[Compare_lists] Checking model list:')
    for model in ml:
        if model in mlr:
            logging.info("[Compare_lists] " + model + " is still being recorded")
            logging.debug("[Compare_lists] Removing " + model + " model")
        else:
            logging.debug("[Compare_lists] " + model + " is online")
            ml_new.append(model)
    logging.debug("[Compare_lists] List of models after comparing:" + str(ml_new))
    return ml_new
