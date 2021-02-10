import ubiops as api
import requests
import json
from json import JSONDecodeError

from pkg.version import VERSION
from pkg.utils import Config


def do_call(_type, api_endpoint, path, data=None, headers=None):
    url = "%s%s" % (api_endpoint, path)
    default_headers = {"Content-Type": "application/json", "accept": "application/json"}

    if headers is None:
        headers = default_headers
    else:
        headers = {**default_headers, **headers}

    if _type == 'post':
        response = requests.post(url, data=json.dumps(data), headers=headers)
    elif _type == 'get':
        response = requests.get(url, headers=headers)
    else:
        raise NotImplementedError("Unknown request type %s" % str(_type))

    try:
        response = json.loads(response.text)
    except JSONDecodeError:
        raise Exception("Could not access %s" % api_endpoint)
    return response


def sign_in(api_endpoint, email):
    data = {"email": email}
    response = do_call("post", api_endpoint, "/oauth/sign-in", data=data)
    assert 'error' not in response, response['error']
    assert 'provider' in response, "Could not authorize."
    assert 'url' in response, "Could not authorize."
    return response['provider'], response['url']


def authorize(api_endpoint, email, password):
    data = {"email": email, "password": password}
    response = do_call("post", api_endpoint, "/authorize", data=data)

    if 'error' in response and "two factor authentication" in response['error']:
        return False
    elif 'error' in response:
        raise AssertionError(response['error'])

    assert 'access' in response, "Could not authorize."

    user_config = Config()
    user_config.set('auth.api', api_endpoint)
    user_config.set('auth.email', email)
    user_config.set('auth.tmp_access_token', response['access'])
    user_config.delete_option('auth.service_token')
    user_config.write()
    return True


def authorize2fa(api_endpoint, email, password, token):
    data = {"email": email, "password": password, "token": token}
    response = do_call("post", api_endpoint, "/authorize", data=data)

    assert 'error' not in response, response['error']
    assert 'access' in response, "Could not authorize."

    user_config = Config()
    user_config.set('auth.api', api_endpoint)
    user_config.set('auth.email', email)
    user_config.set('auth.tmp_access_token', response['access'])
    user_config.delete_option('auth.service_token')
    user_config.write()
    return True


def sign_in_complete(api_endpoint, code, provider):
    data = {"code": code, "provider": provider}
    response = do_call("post", api_endpoint, "/oauth/complete", data=data)
    assert 'error' not in response, response['error']
    assert 'access' in response, "Could not authorize."

    # Get email from token
    token = "Bearer %s" % response['access']
    oauth_user = user(api_endpoint=api_endpoint, token=token)

    user_config = Config()
    user_config.set('auth.api', api_endpoint)
    user_config.set('auth.email', oauth_user['email'])
    user_config.set('auth.tmp_access_token', response['access'])
    user_config.delete_option('auth.service_token')
    user_config.write()
    return oauth_user['email']


def raise_for_status(api_endpoint, token):
    configuration = api.Configuration()
    configuration.host = api_endpoint
    configuration.api_key_prefix['Authorization'] = ''
    configuration.api_key['Authorization'] = token
    client = api.CoreApi(api.ApiClient(configuration))
    client.user_agent = "UbiOps/cli/%s" % VERSION
    assert client.service_status().status == 'ok'
    client.api_client.close()

    # Get email from token
    service_user = user(api_endpoint=api_endpoint, token=token)

    user_config = Config()
    user_config.set('auth.api', api_endpoint)
    user_config.set('auth.email', service_user['email'])
    user_config.set('auth.service_token', token)
    user_config.delete_option('auth.tmp_access_token')
    user_config.write()


def user(api_endpoint, token):
    response = do_call("get", api_endpoint, "/user", headers={"Authorization": token})
    assert 'error' not in response, response['error']
    assert 'email' in response, "Could not authorize."
    return response


def sign_out():
    user_config = Config()
    user_config.delete_option('auth.tmp_access_token')
    user_config.delete_option('auth.service_token')
    user_config.write()
