from __future__ import annotations
from .utils import *
from http import HTTPStatus


class BaseClient:
    AUTH = "auth"
    FILES = "files"
    STREAM = "transfers"
    USERS = "users"
    WORKSPACES = "workspaces"
    RESOURCES = "resources"
    BENCHMARKS = "benchmarks"
    METRICSETS = "metricsets"
    MODELS = "models"
    OPTIMIZERS = "optimizers"
    CRITERIONS = "criterions"
    STRATEGIES = "strategies"
    EXPERIMENTS = "experiments"
    DATA = "data"

    __debug_urls__: bool = False

    @staticmethod
    def set_debug(on: bool = True):
        BaseClient.__debug_urls__ = on

    @staticmethod
    def reset_debug():
        BaseClient.set_debug(False)

    @property
    def base_url(self):
        return f"{self.scheme}://{self.host}:{self.port}"

    @property
    def auth(self):
        return BearerAuth(self.auth_token)

    @property
    def auth_base(self):
        return f'{self.base_url}/{self.AUTH}'

    @property
    def files_base(self):
        return f'{self.base_url}/{self.FILES}'

    @property
    def streaming_base(self):
        return f'{self.base_url}/{self.STREAM}'

    @property
    def users_base(self):
        return f'{self.base_url}/{self.USERS}'

    @property
    def workspaces_base(self):
        return f'{self.users_base}/{self.username}/{self.WORKSPACES}'

    @property
    def data_repositories_base(self):
        return f'{self.workspaces_base}/{self.workspace}/{self.DATA}'

    @property
    def resources_base(self):
        return f"{self.base_url}/{self.RESOURCES}"

    @property
    def benchmarks_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.BENCHMARKS}"

    @property
    def metricsets_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.METRICSETS}"

    @property
    def models_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.MODELS}"

    @property
    def optimizers_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.OPTIMIZERS}"
    
    @property
    def criterions_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.CRITERIONS}"
    
    @property
    def strategies_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.STRATEGIES}"

    @property
    def experiments_base(self):
        return f"{self.workspaces_base}/{self.workspace}/{self.EXPERIMENTS}"
    
    @staticmethod
    def get_url(*args):
        return '/'.join(args) + '/'

    def request(self, method: str, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        if isinstance(url_items, str):
            url = url_items
        elif isinstance(url_items, list):
            url = self.get_url(*url_items)
        else:
            raise TypeError()
        if self.__debug_urls__:
            print(f"Sending request ({method} @ {url}) ...")
        return requests.request(
            method, url,
            params=params, json=data, headers=headers,
            auth=(self.auth if auth else None),
        )

    def get(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('get', url_items, data=data, auth=auth, headers=headers, params=params)

    def post(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('post', url_items, data=data, auth=auth, headers=headers, params=params)

    def put(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('put', url_items, data=data, auth=auth, headers=headers, params=params)

    def patch(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('patch', url_items, data=data, auth=auth, headers=headers, params=params)

    def delete(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('delete', url_items, data=data, auth=auth, headers=headers, params=params)

    def head(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('head', url_items, data=data, auth=auth, headers=headers, params=params)

    def options(self, url_items: str | list[str], data=None, auth=True, headers=None, params=None):
        return self.request('options', url_items, data=data, auth=auth, headers=headers, params=params)

    def __init__(self, host: str = 'localhost', port: int = 5000, scheme: str = 'http'):
        self.scheme = scheme  # 'cached'
        self.host = host  # 'cached'
        self.port = port  # 'cached'
        self.username = None  # 'cached'
        self.workspace = None   # 'cached'
        self.auth_token = None

    def set_user(self, username: str):
        self.username = username

    def set_workspace(self, workspace: str):
        self.workspace = workspace

    def register(self, username: str, email: str, password: str):
        data = {
            'username': username,
            'email': email,
            'password': password,
        }
        url = self.get_url(self.users_base)
        resp = self.post(url, data, auth=False)
        return resp  # resp.status_code, resp.headers, resp.json()

    def login(self, username: str, password: str):
        url = self.get_url(self.auth_base, 'login')
        data = {
            'username': username,
            'password': password,
        }

        resp = self.post(url, data, auth=False)
        data = resp.json()

        if resp.status_code == HTTPStatus.OK:
            self.username = username
            self.auth_token = data.pop('token')
        return resp  # resp.status_code, resp.headers, data

    def logout(self):
        url = self.get_url(self.auth_base, 'logout')
        resp = self.post(url)

        if resp.status_code == HTTPStatus.OK:
            self.auth_token = None
        return resp  # resp.status_code, msg

    def get_user(self, username: str = None):
        if username is None:
            username = self.username
        return self.get([self.users_base, username])

    def edit_user(self, new_username, new_email):
        if (new_username is None) or (new_email is None):
            raise TypeError('New username and email cannot be None!')
        else:
            data = {
                'username': new_username,
                'email': new_email,
            }
            url = self.get_url(self.users_base, self.username)
            return self.patch(url, data)

    def edit_password(self, old_password, new_password):
        if (old_password is None) or (new_password is None):
            raise TypeError('Old and new passwords cannot be None!')
        else:
            data = {
                'old_password': old_password,
                'new_password': new_password,
            }
            return self.patch([self.users_base, self.username, 'password'], data)

    def delete_user(self):
        return self.delete([self.users_base, self.username])

    def create_workspace(self, workspace_name: str):
        data = {
            "name": workspace_name,
        }
        resp = self.post([self.workspaces_base], data)
        if resp.status_code == HTTPStatus.CREATED:
            self.workspace = workspace_name
        return resp

    def get_workspace(self, workspace_name: str = None):
        if workspace_name is None:
            if self.workspace is None:
                raise ValueError("Unknown workspace name")
            else:
                workspace_name = self.workspace
        return self.get([self.workspaces_base, workspace_name])

    def open_workspace(self, workspace_name: str = None):
        if workspace_name is None:
            if self.workspace is None:
                raise ValueError("Unknown workspace name")
            else:
                workspace_name = self.workspace
        return self.patch([self.workspaces_base, workspace_name, 'status'], data={'status': 'OPEN'})

    def close_workspace(self, workspace_name: str = None):
        if workspace_name is None:
            if self.workspace is None:
                raise ValueError("Unknown workspace name")
            else:
                workspace_name = self.workspace
        return self.patch([self.workspaces_base, workspace_name, 'status'], data={'status': 'CLOSED'})

    def delete_workspace(self, workspace_name: str = None):
        if workspace_name is None:
            if self.workspace is None:
                raise ValueError("Unknown workspace name")
            else:
                workspace_name = self.workspace
        return self.delete([self.workspaces_base, workspace_name])

    # Data Repositories
    def create_data_repository(self, repo_name: str, repo_desc: str = None):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        else:
            return self.post([self.data_repositories_base], data={'name': repo_name, 'description': repo_desc})

    def get_data_repository(self, repo_name: str):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        else:
            return self.get([self.data_repositories_base, repo_name])

    def get_data_repository_desc(self, repo_name: str):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        else:
            return self.get([self.data_repositories_base, repo_name, 'desc'])

    def delete_data_repository(self, repo_name: str):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        else:
            return self.delete([self.data_repositories_base, repo_name])

    def create_subdir(self, repo_name: str, folder_name: str, folder_path: list[str] = None):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        folder_path = [] if folder_path is None else folder_path
        data = {
            'name': folder_name,
            'path': '/'.join(folder_path),
        }
        return self.post([self.data_repositories_base, repo_name, 'folders'], data=data)

    def move_subdir(self, repo_name: str, src_path: str, dest_path: str):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        data = {
            'src_path': src_path,
            'dest_path': dest_path,
        }
        return self.patch([self.data_repositories_base, repo_name, 'folders'], data=data)

    def delete_subdir(self, repo_name: str, path: str):
        if repo_name is None:
            raise ValueError("Repository name cannot be None.")
        return self.delete([self.data_repositories_base, repo_name, 'folders', path])

    # TODO send files!

    # Generic Resources TODO Modificare!
    def add_generic_resource(self, name: str, typename: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'type': typename,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post([self.resources_base, self.username, self.workspace], data=data)

    def build_generic_resource(self, name: str, typename: str):
        return self.get([self.resources_base, self.username, self.workspace, typename, name])

    def delete_generic_resource(self, name: str, typename: str):
        return self.delete([self.resources_base, self.username, self.workspace, typename, name])

    # Benchmarks
    def create_benchmark(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.benchmarks_base, data=data)

    def build_benchmark(self, name: str):
        return self.get([self.benchmarks_base, name])

    def rename_benchmark(self, name: str, new_name: str):
        return self.update_benchmark(name, {'name': new_name})

    def update_benchmark(self, name: str, updata: dict):
        return self.patch([self.benchmarks_base, name], data=updata)

    def delete_benchmark(self, name: str):
        return self.delete([self.benchmarks_base, name])

    # MetricSets
    def create_metric_set(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.metricsets_base, data=data)

    def build_metric_set(self, name: str):
        return self.get([self.metricsets_base, name])

    def rename_metric_set(self, name: str, new_name: str):
        return self.update_metric_set(name, {'name': new_name})

    def update_metric_set(self, name: str, updata: dict):
        return self.patch([self.metricsets_base, name], data=updata)

    def delete_metric_set(self, name: str):
        return self.delete([self.metricsets_base, name])

    # Models
    def create_model(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.models_base, data=data)

    def build_model(self, name: str):
        return self.get([self.models_base, name])

    def rename_model(self, name: str, new_name: str):
        return self.update_model(name, {'name': new_name})

    def update_model(self, name: str, updata: dict):
        return self.patch([self.models_base, name], data=updata)

    def delete_model(self, name: str):
        return self.delete([self.models_base, name])

    # Optimizer
    def create_optimizer(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.optimizers_base, data=data)

    def build_optimizer(self, name: str):
        return self.get([self.optimizers_base, name])

    def rename_optimizer(self, name: str, new_name: str):
        return self.update_optimizer(name, {'name': new_name})

    def update_optimizer(self, name: str, updata: dict):
        return self.patch([self.optimizers_base, name], data=updata)

    def delete_optimizer(self, name: str):
        return self.delete([self.optimizers_base, name])

    # Criterions
    def create_criterion(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.criterions_base, data=data)

    def build_criterion(self, name: str):
        return self.get([self.criterions_base, name])

    def rename_criterion(self, name: str, new_name: str):
        return self.update_criterion(name, {'name': new_name})

    def update_criterion(self, name: str, updata: dict):
        return self.patch([self.criterions_base, name], data=updata)

    def delete_criterion(self, name: str):
        return self.delete([self.criterions_base, name])

    # Strategies
    def create_strategy(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.strategies_base, data=data)

    def build_strategy(self, name: str):
        return self.get([self.strategies_base, name])

    def rename_strategy(self, name: str, new_name: str):
        return self.update_strategy(name, {'name': new_name})

    def update_strategy(self, name: str, updata: dict):
        return self.patch([self.strategies_base, name], data=updata)

    def delete_strategy(self, name: str):
        return self.delete([self.strategies_base, name])

    # Experiments
    def create_experiment(self, name: str, build_config_data: dict, description: str = None):
        data = {
            'name': name,
            'build': build_config_data,
        }
        if description is not None:
            data['description'] = description
        return self.post(self.experiments_base, data=data)

    def setup_experiment(self, name: str):
        return self.patch([self.experiments_base, name, 'setup'])

    def start_experiment(self, name: str):
        return self.patch([self.experiments_base, name], data={'status': 'START'})

    def stop_experiment(self, name: str):
        return self.patch([self.experiments_base, name], data={'status': 'STOP'})

    def get_experiment_status(self, name: str):
        return self.get([self.experiments_base, name, 'status'])

    def get_experiment_results(self, name: str):
        return self.get([self.experiments_base, name, 'results'])

    def get_experiment_settings(self, name: str):
        return self.get([self.experiments_base, name, 'settings'])

    def get_experiment_model(self, name: str):
        return self.get([self.experiments_base, name, 'model'])

    def get_experiment_csv_results(self, name: str):
        return self.get([self.experiments_base, name, 'results', 'csv'])

    def delete_experiment(self, name: str):
        return self.delete([self.experiments_base, name])