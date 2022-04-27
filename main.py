from application import *
from mongoengine import NotUniqueError
from flask import jsonify


#   Useful routines
def cls():
    os.system("cls")


def clear():
    os.system("clear")


app = create_app()


@app.errorhandler(Exception)
def return_exception(ex: Exception):
    print(ex)
    msgs = [str(arg) for arg in ex.args]
    resp = jsonify({
        'error': msgs,
    })
    resp.status_code = 500
    return resp


@app.shell_context_processor
def make_shell_context():
    return {
        # generals
        'system': os.system, 'cls': cls, 'clear': clear, 'db': db,

        # classes
        'User': User, 'DataType': DataType,
        'Context': DictUserWorkspaceResourceContext,
        'NotUniqueError': NotUniqueError,
    }


if __name__ == '__main__':
    print('DataType:\n', DataType.get_all_typenames(), '\n')
    app.run('0.0.0.0')