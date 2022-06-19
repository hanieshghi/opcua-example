import os
import sys
import time
from opcua import Client
import requests
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()
sys.path.insert(0, "..")

"""
    This function tries to connect to the server
"""


def connect_to_server(timeout=0):
    try:
        url = os.getenv('ENDPOINT')
        _client = Client(url)

        """
        SET Credentials
        """
        _client.set_user(os.getenv('USERNAME'))
        _client.set_password(os.getenv('PASSWORD'))
        _client.set_security_string("Basic256Sha256,SignAndEncrypt,cert/my_cert.der,cert/my_private_key.pem")
        # client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
        client.secure_channel_timeout = 10000
        client.session_timeout = 10000

        _client.connect()
        print('________________client connected_________________')
        timeout = 0

        return _client

    except KeyboardInterrupt:
        print('\n_______________See You Later!_______________')
        os._exit(0)

    except ConnectionRefusedError:
        print('trying to connect after {} seconds'.format(timeout))
        time.sleep(timeout)
        timeout += 5
        connect_to_server(timeout)

    except Exception as e:
        print("unexpected error in connection", e)
        return False


def start(_client):
    while True:
        try:
            """
                GET NODES
            """
            length_node = _client.get_node('ns=2;s=Miba.catfact.length')
            heartbeat_node = _client.get_node('ns=2;s=Miba.heartbeat')
            fact_node = _client.get_node('ns=2;s=Miba.catfact.fact')

            """
                GET VALUES
            """
            length_value = length_node.get_value()
            heartbeat_value = heartbeat_node.get_value()
            fact_value = fact_node.get_value()

            """
            PRINT DATA
            """
            print_values(heartbeat_value, fact_value, length_value)

            time.sleep(5)

            """
                GET CATFACT DATA through REST REQUEST
            """
            fact, length = get_cat_fact()

            """
                SET LENGTH and FACT values
            """
            length_node.set_value(length)
            fact_node.set_value(fact)

        except KeyboardInterrupt:
            print('\n_______________See You Later!_______________')
            _client.disconnect()
            os._exit(0)

        except Exception as e:
            print('\n_________connection Interrupted________', e)
            _client = connect_to_server()


def draw_cat():
    print(Fore.GREEN + " ,_     _")
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


def get_cat_fact():
    try:
        """
            make REST call to fetch CAT_DATA
        """
        url = os.getenv('CAT_FACT_URL')
        data = requests.get(url)
        if not data.status_code or data.status_code != 200:
            print('cannot get catfact. error: {}'.format(data.json()))
            os._exit(1)
        else:
            catfact = data.json()
            return catfact['fact'], catfact['length']
    except Exception as e:
        print('exception in geting catfact. error: {}'.format(e))
        os._exit(1)


def print_values(heartbeat, fact, length):
    # clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    # draw a cute cat
    draw_cat()
    # print values
    print(Style.BRIGHT + Fore.RED + 'Length: ', length)
    print(Style.RESET_ALL)
    print(Fore.YELLOW + 'Fact: ', fact)
    print(Style.RESET_ALL)


if __name__ == "__main__":
    client = None
    while client is None:
        client = connect_to_server()
    if not client:
        print("error in connection")
        os._exit(1)
    start(client)
