import requests
import json
import os
import configparser

from pprint import pprint


#API="znmvgrccmkkynmfez3k2mcjxfgbhk95h"
URL="api.sherpadesk.com"
INSKEY = ""
ORGKEY = ""
CONFIGPATH = os.path.expanduser("~/sherpa.ini")
CONFIG = ""

def GetInstance_OrgKey():
    global INSKEY, ORGKEY, CONFIG

    orgurl = 'https://x:{}@{}/organizations/?format=json'.format(CONFIG['SHERPA']['APIKEY'], CONFIG['SHERPA']['URL'])

    try:
        response = requests.get(orgurl)
        response.raise_for_status()
    except requests.RequestException as e:
        print(e)
        quit(1)

    responsej = response.json()

    ORGKEY = responsej[0]['key']
    INSKEY = responsej[0]['instances'][0]['key']

    return

def GetOpenTickets():
    global INSKEY, ORGKEY, CONFIG

    url = 'https://{}-{}x:{}@{}/tickets?status=open&role=tech&format=json'.format(ORGKEY,INSKEY,CONFIG['SHERPA']['APIKEY'],CONFIG['SHERPA']['URL'])
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.RequestException as e:
        print(e)

    return res.json()


def TimeOnTicket(key):
    global INSKEY, ORGKEY, CONFIG
    url = 'https://{}-{}x:{}@{}/time'.format(ORGKEY, INSKEY, CONFIG['SHERPA']['APIKEY'], CONFIG['SHERPA']['URL'])
    time = input("How much time? In float format 1 and half hours = 1.5 :")
    payload = json.dumps({
        "ticket_key": key,
        "hours": time
    })
    try:
        res = requests.post(url,payload,headers={'content-type': 'application/json'})
        res.raise_for_status()
    except requests.RequestException as e:
        print(e)
        quit(1)

    return


def CloseTicket(key):
    global INSKEY, ORGKEY, CONFIG
    url = 'https://{}-{}x:{}@{}/tickets/{}'.format(ORGKEY, INSKEY, CONFIG['SHERPA']['APIKEY'], CONFIG['SHERPA']['URL'],key)
    note = input("Confirmation message? ")
    payload = json.dumps({
        "status": "closed",
        "note_text": note,
        "is_send_notifications": False,
        "resolved": True,
        "confirmed": True,
        "confirm_note": "confirmed by me"
    })
    try:
        res = requests.put(url,payload,headers={'content-type': 'application/json'})
        res.raise_for_status()
    except requests.RequestException as e:
        print(e)
        quit(1)

def FirstTime():
    global CONFIGPATH
    print("-" * 70)
    print("Can not find your config file.. First time?")
    print("Lets create one at: {}".format(CONFIGPATH))
    print("-" * 70)
    config = configparser.ConfigParser()
    config['DEFAULT']={'URL':'api.sherpadesk.com'}
    config['SHERPA'] = {}
    print("Need your API token from sherpadesk. This is found in you Profile page.")
    config['SHERPA']['APIKEY'] = input("API token:")
    try:
        cf = open(CONFIGPATH, 'x')
    except os.error as e:
        print(e)

    config.write(cf)

    return

def main():
    global CONFIGPATH,CONFIG


    if not os.path.exists(CONFIGPATH):
        FirstTime()

    CONFIG = configparser.ConfigParser()

    #CONFIG = tempconfig.read(CONFIGPATH)
    CONFIG.read(CONFIGPATH)

    GetInstance_OrgKey()

    r = GetOpenTickets()

    for tickets in r:
        print("\n" * 200)

        #pprint(tickets)
        print("-" * 70)
        print("{}\t{}\t\t{}\n{}".format(tickets['user_email'],
                                        tickets['subject'],
                                        tickets['days_old'],
                                        str(tickets['initial_post']).replace('<br>', '\n')))
        closeit = input("=" * 58 +"Close Y/[N]:")

        if closeit == "y":
            TimeOnTicket(tickets['key'])
            CloseTicket(tickets['key'])


    #pprint(r)




if __name__ == '__main__':
    main()
