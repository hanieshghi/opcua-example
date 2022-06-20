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


def server_setup():
    """
        SERVER SETUP
    """
    server_name = os.getenv('SERVER_NAME')
    name_space = os.getenv('SERVER_NAMESPACE')
    url = os.getenv('ENDPOINT')

    _server = Server()
    _server.set_server_name(server_name)
    address_space = _server.register_namespace(name_space)
    _server.set_endpoint(url)

    # set server security policy
    _server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    _server.load_certificate('cert/my_cert.der')
    _server.load_private_key('cert/my_private_key.pem')

    #  set user manager
    policy_ids = ["Username"]
    _server.set_security_IDs(policy_ids)
    _server.user_manager.set_user_manager(user_manager)

    """
        SERVER MODELING
    """
    node = _server.get_objects_node()
    miba_object = node.add_object(address_space, 'Miba')
    cat_fact_folder = miba_object.add_folder(address_space, 'catFact')

    """
        add Variables
    """
    fact_identifier = 'ns={};s=Miba.catfact.fact;'.format(address_space)
    length_identifier = 'ns={};s=Miba.catfact.length;'.format(address_space)
    heartbeat_identifier = 'ns={};s=Miba.heartbeat;'.format(address_space)

    _fact = cat_fact_folder.add_variable(fact_identifier, 'fact', '', ua.VariantType.String)
    _length = cat_fact_folder.add_variable(length_identifier, 'length', 0, ua.VariantType.Int64)
    _heartbeat = miba_object.add_variable(heartbeat_identifier, 'heartbeat', True, ua.VariantType.Boolean)

    #  fact and length should be writable to be changed by client
    _fact.set_writable()
    _length.set_writable()

    #  start server
    _server.start()
    return _server, _heartbeat, _fact, _length


if __name__ == "__main__":
    server, heartbeat, fact, length = server_setup()
    try:
        while True:
            heartbeat_value = heartbeat.get_value()
            print_values(heartbeat_value, fact.get_value(), length.get_value())
            heartbeat.set_value(not heartbeat_value)
            time.sleep(1)
    except KeyboardInterrupt:
        print('_______________________server stopped_________________________')
        server.stop()
