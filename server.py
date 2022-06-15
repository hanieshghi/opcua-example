import time
import os
from opcua import Server, ua
from opcua.server.user_manager import UserManager
import sys

from dotenv import load_dotenv
load_dotenv()

from colorama import init, Fore, Back, Style
init()

from prettytable.colortable import ColorTable, Themes
x = ColorTable(theme=Themes.OCEAN)
sys.path.insert(0, "..")


"""
    setup for authentication
"""
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
users_db = {user: password}


def user_manager(isession, username, password):
    isession.user = UserManager.User
    return username in users_db and password == users_db[username]
##########


def printValues(_heartbeat, fact, length):
    x.field_names = ["Heartbeat", "Length", "fact"]
    if _heartbeat:
        hearbeat2 = Back.CYAN + Fore.BLACK + 'ALIVE :)'
    else:
        hearbeat2 = Back.RED + Fore.BLACK + 'DEAD :('

    x.add_row([hearbeat2, length, fact[:20]])
    x.border = True
    
    print(x)
    

if __name__ == "__main__":
    """
        SERVER SETUP
    """
    server = Server()
    serverName = "MIBA_SERVER_TEST"
    server.set_server_name(serverName)
    addressSpace = server.register_namespace('URI:urn:example.org:FreeOpcUa:python-opcua')

    # set server security policy
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    server.load_certificate('cert/my_cert.der')
    server.load_private_key('cert/my_private_key.pem')

    #  set user manager
    policyIDs = ["Username"]
    server.set_security_IDs(policyIDs)
    server.user_manager.set_user_manager(user_manager)

    url = os.getenv('ENDPOINT')
    server.set_endpoint(url)

    """
        SERVER MODELING
    """
    node = server.get_objects_node()
    mibaObject = node.add_object(addressSpace, 'Miba')
    catFactFolder = mibaObject.add_folder(addressSpace, 'catFact')

    """
        add Variables
    """
    factIdentifier = 'ns={};s=Miba.catfact.fact;'.format(addressSpace)
    lengthIdentifier = 'ns={};s=Miba.catfact.length;'.format(addressSpace)
    heartbeatIdentifier = 'ns={};s=Miba.heartbeat;'.format(addressSpace)

    fact = catFactFolder.add_variable(factIdentifier, 'fact', '', ua.VariantType.String)
    length = catFactFolder.add_variable(lengthIdentifier, 'length', 0, ua.VariantType.Int64)
    hearbeat = mibaObject.add_variable(heartbeatIdentifier, 'hearbeat', True, ua.VariantType.Boolean)

    #  fact and length should be writable to be changed from client
    fact.set_writable()
    length.set_writable()

    #  start server
    server.start()
    try:
        while True:
            _heartbeat = hearbeat.get_value()
            printValues(_heartbeat, fact.get_value(), length.get_value())
            hearbeat.set_value(not _heartbeat)
            time.sleep(1)
    except KeyboardInterrupt:
        print('_______________________server stopped_________________________')
        server.stop()
