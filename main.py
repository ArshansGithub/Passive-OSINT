import requests
import asyncio
import websockets
import json
import random
import string
import warnings

warnings.filterwarnings("ignore")

def duplicate(list):
    newList = []
    for i in range(len(list)):
        if list[i] not in newList:
            newList.append(list[i])
    return newList


def run(email, address, fullname, birthyear):
    session = requests.Session()


    scannedAddresses = []
    scannedEmails = []
    scannedNumbers = []
    scannedRelatives = []
    scannedAliases = []
    responses = []

    getCookie = session.options("https://api.dataseal.io/validate/address").cookies
    checkAddress = session.post("https://api.dataseal.io/validate/address", data='{"address": "' + address + '"}', cookies=getCookie)
    if not checkAddress.json()['code'] == 200:
        print("Invalid Address")
        exit()
    createScan = session.post("https://api.dataseal.io/scans", data=f'{{"profiles":[{{"email":"{email}","fullname":"{fullname}","birthYear":"{birthyear}","location":"{address}","isOwner":true}}]}}', cookies=getCookie)
    if not createScan.json()['code'] == 201:
        print("Invalid data")
        exit()
    else:
        createScan = createScan.json()['body']['scans'][0]
    formattedCookie = "PHPSESSID=" + requests.utils.dict_from_cookiejar(getCookie)['PHPSESSID'] + ";"
    print("[!] Scanning...")
    async def scan():
        async with websockets.connect("wss://px.dataseal.io/", extra_headers={"Cookie": formattedCookie}) as websocket:
            await websocket.send(f'{{"event":"subscribe","channels":["{createScan}"]}}')
            while len(responses) < 60:
                responses.append(await websocket.recv())
                #print("added response")
            websocket.close()    
            for e in responses:
                message = json.loads(e)
                if message['event'] == "record":
                    if message['payload']['profile']['name']['display'] not in scannedAliases:
                        scannedAliases.append(message['payload']['profile']['name']['display'])
                        #print("Added alias")
                    for i in range(len(message['payload']['profile']['addresses'])):
                        if not message['payload']['profile']['addresses'][i]['street'] == None:
                            if message['payload']['profile']['addresses'][i]['street'] not in scannedAddresses:
                                scannedAddresses.append(message['payload']['profile']['addresses'][i]['street'])
                                #print('Added address')
                    for i in range(len(message['payload']['profile']['phones'])):
                        if message['payload']['profile']['phones'][i]['display'] not in scannedNumbers:
                            scannedNumbers.append(message['payload']['profile']['phones'][i]['display'])
                            #print('Added phone')
                    for i in range(len(message['payload']['profile']['relatives'])):
                        if message['payload']['profile']['relatives'][i]['display'] not in scannedRelatives:
                            scannedRelatives.append(message['payload']['profile']['relatives'][i]['display'])
                            #print('Added relative')
                    for i in range(len(message['payload']['profile']['emails'])):
                        if message['payload']['profile']['emails'][i]['display'] not in scannedEmails:
                            scannedEmails.append(message['payload']['profile']['emails'][i]['display'])
                            #print('Added email')
                                    
        
                    

    asyncio.get_event_loop().run_until_complete(scan())
    return scannedAddresses, scannedEmails, scannedNumbers, scannedRelatives, scannedAliases

randomEmail = ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + "@gmail.com"
locate = input("Location: ")
name = input("Full name: ")
dob = input("Year of DOB: ")
address1, email1, number1, relative1, aliases1 = run(randomEmail, locate, name, dob)
address2, email2, number2, relative2, aliases2 = run(randomEmail, locate, name, dob)
print("[!] Finished scanning, now sorting...")
reportAddresses = duplicate(duplicate(address1) + duplicate(address2))
reportEmails = duplicate(duplicate(email1) + duplicate(email2))
reportNumbers = duplicate(duplicate(number1) + duplicate(number2))
reportRelatives = duplicate(duplicate(relative1) + duplicate(relative2))
reportAliases = duplicate(duplicate(aliases1) + duplicate(aliases2))

print("[!] Writing report...")
with open("report.txt", "w") as file:
    file.write("="*50 + "\n" + "="*16 + "Made by Arshan" + "=" * 16 + "\n" + "="*50 + "\n\n" + "-" * 18 + "Found Aliases!" + "-" * 18 + "\n\n")
    if reportAliases == []:
        file.write("[!]" + " " * 12 + "No aliases found\n")
    else:
        for i,e in enumerate(reportAliases):
            file.write(f"[{i}]" + " "*12 + e + "\n")
    
    file.write("\n" + "-" * 17 + "Found addresses!" + "-" * 17 + "\n\n")
    if reportAddresses == []:
        file.write("[!]" + " " * 12 + "No addresses found\n")
    else:
        for i,e in enumerate(reportAddresses):
            file.write(f"[{i}]" + " "*12 + e + "\n")
    
    file.write("\n" + "-" * 14 + "Found email addresses!" + "-" * 14 + "\n\n")
    if reportEmails == []:
        file.write("[!]" + " " * 12 + "No emails found\n")
    else:
        for i,e in enumerate(reportEmails):
            file.write(f"[{i}]" + " "*12 + e + "\n")
    file.write("\n" + "-" * 15 + "Found Phone Numbers!" + "-" * 15 + "\n\n")
    if reportNumbers == []:
        file.write("[!]" + " " * 12 + "No phone numbers found\n")
    else:
        for i,e in enumerate(reportNumbers):
            file.write(f"[{i}]" + " "*12 + e + "\n")
    file.write("\n" + "-" * 17 + "Found Relatives!" + "-" * 17 + "\n\n")
    if reportRelatives == []:
        file.write("[!]" + " " * 12 + "No relatives found\n")
    else:
        for i,e in enumerate(reportRelatives):
            file.write(f"[{i}]" + " "*12 + e + "\n")
    file.write("="*50 + "\n" + "="*16 + "Made by Arshan" + "=" * 16 + "\n" + "="*50)
    file.close()

print("[!] Report written to report.txt")
