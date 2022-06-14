import time
from opcua import Server, ua
from opcua.server.user_manager import UserManager
import sys


sys.path.insert(0, "..")
# setup for username and password
users_db = {"miba": "1234$"}


def user_manager(isession, username, password):
    isession.user = UserManager.User
    return username in users_db and password == users_db[username]


if __name__ == "__main__":
    server = Server()

    serverName = "MIBA_SERVER_TEST"
    server.set_server_name(serverName)
    addressSpace = server.register_namespace('URI:urn:example.org:FreeOpcUa:python-opcua')

    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    server.load_certificate('my_cert.der')
    server.load_private_key('my_private_key.pem')



    policyIDs = ["Username"]
    server.set_security_IDs(policyIDs)
    server.user_manager.set_user_manager(user_manager)
    # server.allow_remote_admin(False)
    url = 'opc.tcp://127.0.0.1:4842'
    server.set_endpoint(url)
    print(server.get_root_node())
    node = server.get_objects_node()

    mibaObject = node.add_object(addressSpace, 'Miba')

    catFactFolder = mibaObject.add_folder(addressSpace, 'catFact')
    fact = catFactFolder.add_variable('ns={};s=Miba.catfact.fact;'.format(addressSpace), 'fact', 'inital string',
                                      ua.VariantType.String)
    length = catFactFolder.add_variable('ns={};s=Miba.catfact.length;'.format(addressSpace), 'length', 0,
                                        ua.VariantType.Int64)

    hearbeat = mibaObject.add_variable('ns={};s=Miba.heartbeat;'.format(addressSpace), 'hearbeat', False,
                                       ua.VariantType.Boolean)

    fact.set_writable()
    length.set_writable()

    server.start()

    try:
        while True:
            _heartbeat = hearbeat.get_value()
            hearbeat.set_value(not _heartbeat)
            time.sleep(1)
    except KeyboardInterrupt:
        print('server stopped')
        server.stop()
