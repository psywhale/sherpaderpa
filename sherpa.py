import requests
import json
import os, sys
import configparser
from pprint import pprint
import urwid


INSKEY = ""
ORGKEY = ""
CONFIGPATH = os.path.expanduser("~/sherpa.ini")
CONFIG = ""


def ClearScreen():
    print("\033[H\033[J")




def GetInstance_OrgKey():
    global INSKEY, ORGKEY, CONFIG

    orgurl = 'https://x:{}@{}/organizations/?format=json'.format(CONFIG['SHERPA']['APIKEY'], CONFIG['SHERPA']['URL'])

    try:
        response = requests.get(orgurl)
        response.raise_for_status()
    except requests.RequestException as e:
        print(e)
        sys.exit(1)

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
        sys.exit(1)

    return


def CloseTicket(key,note):
    global INSKEY, ORGKEY, CONFIG
    url = 'https://{}-{}x:{}@{}/tickets/{}'.format(ORGKEY, INSKEY, CONFIG['SHERPA']['APIKEY'], CONFIG['SHERPA']['URL'],key)

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

def PrintTicket(key):
    global INSKEY, ORGKEY, CONFIG
    url = 'https://{}-{}x:{}@{}/tickets/{}'.format(ORGKEY, INSKEY, CONFIG['SHERPA']['APIKEY'], CONFIG['SHERPA']['URL'],key)


    try:
        res = requests.get(url, headers={'content-type': 'application/json'})
        res.raise_for_status()
    except requests.RequestException as e:
        print(e)
        sys.exit(1)

    return res.json()

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

def MainMenu(title, tickets):
    body = [urwid.Text(title),urwid.Divider()]
    for t in tickets:
        button = urwid.Button(t['subject'],TicketMenu,t['key'])
        body.append(urwid.AttrMap(button,None,focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def CloseMenu(button,ticketdata):
    key = ticketdata[0]
    message = ticketdata[1]
    CloseTicket(key,message)



def TicketMenu(button,key):
    ticket = PrintTicket(key)
    title = [urwid.Text(ticket['subject']), urwid.Divider()]
    body = urwid.Text(ticket['initial_post'])
    close = urwid.Edit("close message",None,True)

    closebtn = urwid.Button('Close Ticket',CloseMenu,[key,close.get_edit_text])

    backbtn = urwid.Button('Back',MainMenu('Tickets',GetOpenTickets())).focus
    bottommenu = [closebtn, urwid.Divider(), backbtn]
    bottom - urwid.Columns(bottommenu)




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
        ClearScreen()
        print("-" * 70 + "\n")
        ticket_body = str(tickets['initial_post']).replace('<br>', '\n')
        if ticket_body.__len__() > 600:
            print("{}\t{}\t\t{}\n".format(tickets['user_email'],
                                            tickets['subject'],
                                            tickets['days_old']))
            details = input("=" * 50 + "  details?:")
            if details == "y":
                singleticket = PrintTicket(tickets['key'])

                print("\n{}\n".format(str(singleticket['initial_post']).replace('<br>', '\n')))
        else:
            print("{}\t{}\t\t{}\n{}".format(tickets['user_email'],
                                        tickets['subject'],
                                        tickets['days_old'],
                                        ticket_body))
        closeit = input("=" * 58 +"Close Y/[N]:")

        if closeit == "y":
            TimeOnTicket(tickets['key'])
            CloseTicket(tickets['key'])


    #pprint(r)


if __name__ == '__main__':

    main()
