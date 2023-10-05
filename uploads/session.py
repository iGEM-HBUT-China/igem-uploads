import mimetypes
import os
import warnings
from pathlib import Path

import prettytable as pt
import requests
from lxml import etree

NOT_LOGGED_IN = 0
LOGGED_IN = 1
LOGGED_FAILED = -1


def check_parameter(directory: str):
    if directory.startswith('/'):
        warnings.warn('You specified a directory name starting with \'/\', which may cause unknown errors')
        exit(1)


class Session:
    requests_session_instance = requests.session()
    status = NOT_LOGGED_IN
    team_id = ''

    def request(self, method: str, url: str, data=None, files=None):
        if self.status != LOGGED_IN:
            warnings.warn('Not logged in, please login first')
            exit(1)
        return self.requests_session_instance.request(method=method, url=url, data=data, files=files)

    def request_team_id(self):
        response = self.requests_session_instance.request('GET', 'https://old.igem.org/aj/session_info?use_my_cookie=1')
        team_list = response.json()['teams']
        if len(team_list) == 0:
            warnings.warn('Not joined any team')
            exit(1)
        main_team = team_list[0]
        team_id = main_team['team_id']
        team_name = main_team['team_name']
        team_status = main_team['team_status']
        team_year = main_team['team_year']
        team_role = main_team['team_role']
        team_role_status = main_team['team_role_status']
        print('Your team:', team_id, team_name, team_year)
        print('Your role:', team_role)
        if team_status != 'Accepted':
            warnings.warn('Your team is not accepted')
        if team_role_status != 'Accepted':
            warnings.warn('Your team role is not accepted')
        return team_id

    def login(self, username: str, password: str):
        """
        login to igem.org
        :param username: your username
        :param password: your password
        """
        data = {
            "username": username,
            "password": password,
            "Login": "Login",
            "return_to": "https://igem.org"
        }
        response = self.requests_session_instance.post('https://old.igem.org/Login2', data=data)
        if response.text.__contains__('successfully'):
            self.status = LOGGED_IN
            self.team_id = self.request_team_id()
        else:
            self.status = LOGGED_FAILED
            tree = etree.HTML(response.text)
            err_info = str(tree.xpath('/html/body/form/div[1]')[0].text).split('.')[0] + '.'
            warnings.warn(err_info)
            exit(1)

    def query(self, directory: str = ''):
        """
        query a files/dirs in specific directory
        :param directory: (optional) directory to query, default to root directory
        :return: list of files, each file/dir as a dict
        """
        check_parameter(directory)
        response = self.request('GET', f'https://shim-s3.igem.org/v1/teams/{self.team_id}/wiki?directory={directory}')
        res = response.json()
        if res['KeyCount'] > 0:
            print(directory if directory != '' else '/', 'found:', res['KeyCount'])
            contents = []
            if res.get('CommonPrefixes', False):
                contents.extend(sorted(res['CommonPrefixes'], key=lambda x: x['Name']))
            if res.get('Contents', False):
                contents.extend(sorted(res['Contents'], key=lambda x: (x['Type'], x['Name'])))
            table = pt.PrettyTable()
            table.field_names = ["Type", "Name", "DirectoryKey/FileURL"]
            for item in contents:
                if item['Type'] == 'Folder':
                    table.add_row(['Folder', item['Name'], item['Key'].split(f'teams/{self.team_id}/wiki/')[-1]])
                else:
                    table.add_row(['File-' + item['Type'], item['Name'], item['Location']])
            print(table)
            return contents
        elif res['KeyCount'] == 0:
            print(directory if directory != '' else '/', 'found:', res['KeyCount'])
            return []
        else:
            warnings.warn('Query failed')
            exit(1)

    def upload(self, abs_file_path: str, directory: str = '', list_files: bool = True):
        """
        upload file to specific directory
        :param abs_file_path: absolute path of file
        :param directory: (optional) target directory, default to root directory
        :param list_files: (optional) need to list files after upload, default to True
        :type list_files: bool
        :return: file url
        """
        check_parameter(directory)
        if directory == '/':
            warnings.warn('You specified \'/\' as a directory name, which may cause unknown errors')
            exit(1)
        path_to_file = Path(abs_file_path)
        if not path_to_file.is_file():
            warnings.warn('Invalid file path: ' + abs_file_path)
            exit(1)
        mime_type = mimetypes.guess_type(abs_file_path, True)[0]
        data = {
            'directory': directory
        }
        files = {
            'file': (path_to_file.name, open(abs_file_path, 'rb'), mime_type)
        }
        res = self.request('POST', f'https://shim-s3.igem.org/v1/teams/{self.team_id}/wiki',
                           data=data, files=files)
        if res.status_code == 201:
            print(path_to_file.name, 'uploaded', res.json()['location'])
            print()
            if list_files:
                self.query(directory)
            return res.json()['location']
        else:
            warnings.warn('Upload failed' + res.text)

    def upload_dir(self, abs_path: str, directory: str = ''):
        """
        upload a directory and its subdirectories to specific directory
        :param abs_path: absolute path of directory
        :param directory: (optional) target directory, default to root directory
        :return: list of files, each file/dir as a dict
        """
        check_parameter(directory)
        if directory == '/':
            warnings.warn('You specified \'/\' as a directory name, which may cause unknown errors')
            exit(1)
        path_to_dir = Path(abs_path)
        if not path_to_dir.is_dir():
            warnings.warn('Invalid directory path: ' + abs_path)
            exit(1)
        file_list = os.listdir(abs_path)
        if directory == '':
            dir_path = path_to_dir.name
        else:
            dir_path = directory + '/' + path_to_dir.name
        for filename in file_list:
            if filename.startswith('.'):
                continue
            if (path_to_dir / filename).is_file():
                self.upload(path_to_dir / filename, dir_path, False)
            if (path_to_dir / filename).is_dir():
                self.upload_dir(path_to_dir / filename, dir_path)
        return self.query(dir_path)

    def delete(self, filename: str, directory: str = '', list_files: bool = True):
        """
        delete file in specific directory
        :param filename: filename
        :param directory: file parent directory, default to root directory
        :param list_files: need to list files after delete, default to True
        """
        check_parameter(directory)
        if directory == '/':
            warnings.warn('You specified \'/\' as a directory name, which may cause unknown errors')
            exit(1)
        res = self.request('DELETE',
                           f'https://shim-s3.igem.org/v1/teams/{self.team_id}/wiki/{filename}?directory={directory}')
        if res.status_code == 200:
            print(directory + '/' + filename, 'deleted')
            print()
            if list_files:
                self.query(directory)
        else:
            warnings.warn(directory + '/' + filename + ' delete failed')

    def truncate_dir(self, directory: str):
        """
        truncate a directory
        :param directory: directory to truncate
        :return: list files after truncate
        """
        contents = self.query(directory)
        for item in contents:
            if item['Type'] == 'Folder':
                self.truncate_dir(directory + '/' + item['Name'])
            else:
                self.delete(item['Name'], directory, False)
        return self.query(directory)
