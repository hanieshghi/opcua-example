import time
import os
from opcua import Server, ua
from opcua.server.user_manager import UserManager
import sys
from colorama import init, Fore, Back
from prettytable.colortable import ColorTable, Themes
from dotenv import load_dotenv

load_dotenv()
init()

x = ColorTable(theme=Themes.OCEAN)
sys.path.insert(0, "..")


"""
    setup for authentication
"""
user = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
users_db = {user: password}


def user_manager(isession, _username, _password):
    isession.user = UserManager.User
    return _username in users_db and _password == users_db[_username]


def print_values(_heartbeat, _fact, _length):
    x.field_names = ["Heartbeat", "Length", "fact"]
    if _heartbeat:
        heartbeat_style = Back.CYAN + Fore.BLACK + 'ALIVE :)'
    else:
        heartbeat_style = Back.RED + Fore.BLACK + 'DEAD :('

    x.add_row([heartbeat_style, _length, _fact[:20]])
    x.border = True
    
    print(x)
    

if __name__ == "__main__":
    """
        SERVER SETUP
    """
    serverName = os.getenv('SERVER_NAME')
    nameSpace = os.getenv('SERVER_NAMESPACE')
    url = os.getenv('ENDPOINT')

    server = Server()
    server.set_server_name(serverName)
    addressSpace = server.register_namespace(nameSpace)
    server.set_endpoint(url)

    # set server security policy
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    server.load_certificate('cert/my_cert.der')
    server.load_private_key('cert/my_private_key.pem')

    #  set user manager
    policyIDs = ["Username"]
    server.set_security_IDs(policyIDs)
    server.user_manager.set_user_manager(user_manager)

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
    heartbeat = mibaObject.add_variable(heartbeatIdentifier, 'heartbeat', True, ua.VariantType.Boolean)

    #  fact and length should be writable to be changed from client
    fact.set_writable()
    length.set_writable()

    #  start server
    server.start()
    try:
        while True:
            _heartbeat = heartbeat.get_value()
            print_values(_heartbeat, fact.get_value(), length.get_value())
            heartbeat.set_value(not _heartbeat)
            time.sleep(1)
    except KeyboardInterrupt:
        print('_______________________server stopped_________________________')
        server.stop()
