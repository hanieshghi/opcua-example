from ast import For
import os
import sys
import time
from opcua import Client
import requests
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from termcolor import colored
load_dotenv()
sys.path.insert(0, "..")


"""
    This function tries to connect to the server
"""
def connectToServer(timeout=0):
    try:
        url = os.getenv('ENDPOINT')
        client = Client(url)

        """
        SET Credentials
        """
        client.set_user(os.getenv('USERNAME'))
        client.set_password(os.getenv('PASSWORD'))
        client.set_security_string("Basic256Sha256,SignAndEncrypt,cert/my_cert.der,cert/my_private_key.pem")
        # client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
        # client.secure_channel_timeout = 10000
        # client.session_timeout = 10000

        client.connect()
        print('________________client connected_________________')
        timeout = 0

        return client

    except KeyboardInterrupt:
        print('\n_______________See You Later!_______________')
        os._exit(0)

    except ConnectionRefusedError:
        print('trying to connect after {} seconds'.format(timeout))
        time.sleep(timeout)
        timeout += 5
        connectToServer(timeout)

    except Exception as e:
        print("unexpected error", e)
        return False


def start(_client):
    while True:
        try:
            """
                GET NODES
            """
            lengthNode = _client.get_node('ns=2;s=Miba.catfact.length')
            heartbeatNode = _client.get_node('ns=2;s=Miba.heartbeat')
            factNode = _client.get_node('ns=2;s=Miba.catfact.fact')

            """
                GET CATFACT DATA through REST REQUEST
            """
            fact, length = getCatFact()

            """
                SET LENGTH and FACT values
            """
            lengthNode.set_value(length)
            factNode.set_value(fact)


            """
                GET VALUES
            """
            lengthValue = lengthNode.get_value()
            heartbeatValue = heartbeatNode.get_value()
            factValue = factNode.get_value()

            
            """
            PRINT DATA
            """
            printValues(heartbeatValue, factValue, lengthValue)

            time.sleep(5)

        except KeyboardInterrupt:
            print('\n_______________See You Later!_______________')
            _client.disconnect()
            os._exit(0)

        except Exception as e:
            print('\n_________connection Interrupted________', e)
            _client = connectToServer()


def drawCat():
    print(Fore.GREEN+" ,_     _")
    print("  |\\_,-~/")
    print(" / _  _ |    ,--.")
    print("(  @  @ )   / ,-'")
    print(" \  T/-._( (")
    print(' /         `. ')
    print("|         _  \ |")
    print(" \ \ ,  /      |")
    print("  || |-\_   /")
    print(" ((/`(_,-'")
    print(Style.RESET_ALL)


"""
    this function fetches CAT DATA through REST request
"""
def getCatFact():
    try:
        url = os.getenv('CAT_FACT_URL')
        data = requests.get(url)
        if not data.status_code or data.status_code != 200:
            print('cannot get catfact. error: {}'.format(data.json()))
            os._exit(0)
        else:
            catfact = data.json()
            return catfact['fact'], catfact['length']
    except Exception as e:
        print('exception in geting catfact. error: {}'.format(e))
        os._exit(0)


def printValues(heartbeat, fact, length):
    # clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    # draw a cute cat
    drawCat()
    # print values
    print(Style.BRIGHT+Fore.RED+'Length: ', length)
    print(Style.RESET_ALL)
    print(Fore.YELLOW+'Fact: ', fact)
    print(Style.RESET_ALL)
    

if __name__ == "__main__":
    client = None
    while client == None:
        client = connectToServer()
    if not client:
        print("error in connection")
        os._exit(0)
    start(client)
