"""
User handling routes.
"""
import os
from flask import Blueprint, request
from mongoengine import NotUniqueError
from application.auth import token_auth
from application.utils import *
from application.models import *
from application.errors import *
from application.validation import *
from http import HTTPStatus

_CHECK_DNS = os.environ.get('EMAIL_VALIDATION_CHECK_DNS') or False

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.app_errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    print(type(error))
    return InternalFailure(str(error))


@bp.app_errorhandler(HTTPStatus.SERVICE_UNAVAILABLE)
def service_unavailable(error):
    print(type(error))
    return ServiceUnavailable(str(error))


@bp.route('', methods=[POST])
@bp.route('/', methods=[POST])
def register():
    """
    Registers a new user.

    RequestSyntax:

    {
        "username": "<username>",
        "email": "<email>",
        "password": "<password>"
    }

    ResponseSyntax (on success):
    status: CREATED

    {
        "message": "User <username> successfully registered."
    }

    :return:
    """

    data, error, opts, extras = checked_json(request, False, {'username', 'email', 'password'})
    if error:
        if data:
            return error(**data)
        else:
            return error()
    else:
        username = data['username']
        email = data['email']
        password = data['password']
        
        result, msg = validate_username(username)
        if not result:
            return InvalidUsername(msg)

        result, msg = validate_password(password)
        if not result:
            return InvalidPassword(msg)

        if User.get_by_name(username) is not None:
            return ExistingUser(user=username)
        elif User.get_by_email(email) is not None:
            return InvalidParameterValue(msg=f"Email '{email}' already in use.")
        else:
            user = User.create(username, email, password)
            return make_success_kwargs(HTTPStatus.CREATED, f"User '{user.username}' correctly registered.")


@bp.route('', methods=[GET])
@bp.route('/', methods=[GET])
@token_auth.login_required
def get_all_users():    # TODO Remove
    """
    Retrieves all users.

    RequestSyntax: {}

    ResponseSyntax (on success):

    {
        "message": "Request successfully completed.",
        "<username1>": "<user_json>",
        "<username2>": "<user_json>",
        ...
    }

    :return:
    """

    all_users = User.all()
    if len(all_users) == 0:
        return make_success_kwargs(HTTPStatus.NO_CONTENT, "No user registered.")
    else:
        data = {}
        for user in all_users:
            data[user.username] = user.to_dict()
        return make_success_kwargs(HTTPStatus.OK, **data)


@bp.route('/<user:username>', methods=[GET])
@bp.route('/<user:username>/', methods=[GET])
@token_auth.login_required
def get_user(username):
    """
    Retrieves a user.

    RequestSyntax: {}

    ResponseSyntax (on success):
    {
        "message": "Request successfully completed.",
        <user_json>
    }

    :param username: Username.
    :return:
    """

    current_user = token_auth.current_user()
    user = User.get_by_name(username)
    if not user:
        return NotExistingUser(user=username)
    else:
        include_email = (current_user.username == username)
        return make_success_dict(HTTPStatus.OK, user.to_dict(include_email=include_email))


@bp.route('/<user:username>', methods=[PATCH])
@bp.route('/<user:username>/', methods=[PATCH])
@token_auth.login_required
def edit_user(username):
    """
    Edits username/email.

    RequestSyntax:

    {
        ["username": "<new_username>"],
        ["email": "<new_email>"]
    }
    
    ResponseSyntax (on success):
    
    {
        ["username": {
            "before": "<old_username>",
            "after": "<after_username>"
        }],
        ["email": {
            "before": "<old_email>",
            "after": "<after_email>"
        }]
    }
    
    :param username:
    :return:
    """

    data, error, opts, extras = checked_json(request, False, required=None, optionals={'username', 'email'})

    if error:
        if data:
            return error(**data)
        else:
            return error()

    hasUsername = False
    email = ''

    if 'username' in opts:
        hasUsername = True
        result, msg = validate_username(data['username'])
        if not result:
            return InvalidUsername(msg)

    if 'email' in opts:
        email = data['email']
        result, msg = validate_email(email, _CHECK_DNS)
        if not result:
            return InvalidEmail(msg)

    current_user = token_auth.current_user()
    if (hasUsername and current_user.username != username) or ((not hasUsername) and current_user.email != email):
        return ForbiddenOperation("You don't have permission to modify another user profile, either because your"
                                  " username or your email or both do not match.")
    else:
        try:
            result = current_user.edit(data)
            if len(result) == 0:
                return make_success_kwargs(HTTPStatus.NOT_MODIFIED)
            else:
                return make_success_kwargs(HTTPStatus.OK, f"User {username} successfully updated.", **result)
        except NotUniqueError as nue:
            print(nue)
            return ForbiddenOperation("Username or email are in use by another profile.")


@bp.route('/<user:username>/password', methods=[PATCH])
@bp.route('/<user:username>/password/', methods=[PATCH])
@token_auth.login_required
def edit_password(username):
    """
    Edits user password.

    RequestSyntax:

    {
        "old_password": "<old_password>",
        "new_password": "<new_password>"
    }

    ResponseSyntax (on success): {
        "message": "Request successfully completed."
    }

    :param username: Username.
    :return:
    """

    data, error, opts, extras = checked_json(request, False, {'old_password', 'new_password'})
    if error:
        if data:
            return error(**data)
        else:
            return error()
    else:
        current_user = token_auth.current_user()
        old_password = data['old_password']
        new_password = data['new_password']

        result, msg = validate_password(old_password)
        if not result:
            return InvalidPassword(msg)

        result, msg = validate_password(new_password)
        if not result:
            return InvalidPassword(msg)

        if current_user.username != username:
            return ForbiddenOperation("You cannot change another user's password!")
        elif not current_user.check_correct_password(old_password):
            return InvalidPassword(f"Old password is incorrect.")
        elif old_password == new_password:
            return make_success_kwargs(HTTPStatus.NOT_MODIFIED)
        else:
            current_user.set_password(new_password)
            return make_success_kwargs(HTTPStatus.OK)


@bp.route('/<user:username>', methods=[DELETE])
@bp.route('/<user:username>/', methods=[DELETE])
@token_auth.login_required
def delete_user(username):
    """
    Deletes user.

    RequestSyntax: {}

    ResponseSyntax (on success):

    {
        "message": "User <username> successfully deleted.",
        "username": "<username>"
    }

    :param username:
    :return:
    """

    current_user = token_auth.current_user()
    if current_user.username == username:
        current_user.delete()
        return make_success_kwargs(HTTPStatus.OK, msg=f"User '{username}' successfully deleted.", username=username)
    else:
        return ForbiddenOperation("You don't have the permission to delete another user!")