import requests

from client import *

dummy_name = "DummyTwo"
dummy_desc = "An example of dummy."
dummy_type = "Dummy"
dummy_build = {
    "name": "DummyGen",
    "x": 9,
    "y": "stringa",
    "z": True,
}


superdummy_name = "SuperDummyOne"
superdummy_desc = "An example of super dummy."
superdummy_type = "SuperDummy"
superdummy_build = {
    "name": "SuperDummyGen",
    "bname": "SuperDummyOne",
    "desc": "...",
    "dummy": "DummyTwo",
}


if __name__ == '__main__':

    _SEP_ = '################################################àà'

    def print_response(response):
        print(response.status_code, response.reason, response.json(), _SEP_, sep='\n')

    BaseClient.set_debug()
    cl = BaseClient("192.168.1.120")
    print(cl.__dict__)
    username = 'servator'
    email = 'abc@example.com'
    password = '1234?abcD'
    new_email = 'def@example.com'
    new_password = '4321?abcD'

    # register and login
    print_response(cl.register(username, email, password))
    print_response(cl.login(username, password))

    # user operations
    print_response(cl.get_user(username))
    print_response(cl.edit_user(username, new_email))
    print_response(cl.edit_password(password, new_password))

    # create and get workspaces
    print_response(cl.create_workspace('wspace1'))
    print_response(cl.get_workspace('wspace1'))

    # create resources
    print_response(cl.add_generic_resource(dummy_name, dummy_type, dummy_build, dummy_desc))
    print_response(cl.add_generic_resource(superdummy_name, superdummy_type, superdummy_build, superdummy_desc))

    # build resources
    print_response(cl.build_generic_resource(dummy_name, dummy_type))
    print_response(cl.build_generic_resource(superdummy_name, superdummy_type))

    # delete resources
    print_response(cl.delete_generic_resource(dummy_name, dummy_type))
    print_response(cl.delete_generic_resource(superdummy_name, superdummy_type))

    # workspace close and deletions
    print_response(cl.close_workspace('wspace1'))
    print_response(cl.delete_workspace('wspace1'))
    print_response(cl.delete_user())

    print("Done!")