import os
import sys
import time
from opcua import Client
import requests

sys.path.insert(0,"..")

def connect(timeout=0):
    try:
        url = 'opc.tcp://127.0.0.1:4842'
        client = Client(url)
        client.set_user('miba')
        client.set_password('1234$')

        client.set_security_string("Basic256Sha256,SignAndEncrypt,my_cert.der,my_private_key.pem")
        # client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
        # client.secure_channel_timeout = 10000
        # client.session_timeout = 10000

        client.connect()
        print('client connected')
        timeout = 0
        return client

    except KeyboardInterrupt:
        print('\n_______________See You Later!_______________')
        os._exit(0)
        # client.disconnect()

    except ConnectionRefusedError:
        print('trying to connect after {} seconds'.format(timeout))
        time.sleep(timeout)
        timeout += 5
        connect(timeout)

    except Exception as e:
        print("errorrrr", e)
        return False

def start(client):
    while True:
        try:
            fact, length = getCatFact()
            lengthNode = client.get_node('ns=2;s=Miba.catfact.length')
            lengthValue = lengthNode.get_value()

            heartbeatNode = client.get_node('ns=2;s=Miba.heartbeat')
            heartbeatValue = heartbeatNode.get_value()

            factNode = client.get_node('ns=2;s=Miba.catfact.fact')
            factValue = factNode.get_value()

            print(heartbeatValue, factValue, lengthValue)
            lengthNode.set_value(length)
            factNode.set_value(fact)
            time.sleep(5)
        except KeyboardInterrupt:
            print('\n_______________See You Later!_______________')
            client.disconnect()
            os._exit(0)
        # except SystemExit:
        #     print("here")
        except Exception as e:
            print('\n_________connection Interrupted________',e)
            client = connect()



def getCatFact():
    try:
        url = 'https://catfact.ninja/fact'
        data = requests.get(url)
        if not data.status_code or data.status_code != 200:
            print('cannot get catfact. error: {}'.format(data.json()))
            # raise SystemExit(0)
            os._exit(0)
        else:
            catfact = data.json()
            return catfact['fact'], catfact['length']
    except Exception as e:
        print('exception in geting catfact. error: {}'.format(e))
        os._exit(0)


if __name__ == "__main__":
    client = connect()
    if not client:
        print ("error in connection")
        exit()
    start(client)
