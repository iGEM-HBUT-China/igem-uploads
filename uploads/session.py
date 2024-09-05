import mimetypes
import os
import threading
import warnings
from pathlib import Path

import prettytable as pt
import requests

NOT_LOGGED_IN = 0
LOGGED_IN = 1
LOGGED_FAILED = -1


def check_parameter(directory: str):
    if directory.startswith('/'):
        warnings.warn('You specified a directory name starting with \'/\', which may cause unknown errors')
        exit(1)


def download_single_file(file_url: str, target_dir: str = '', session: requests.Session = None):
    file_name = os.path.basename(file_url)
    file_path = os.path.join(target_dir, file_name)
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return True
    else:
        print(response.content)
        warnings.warn(f'Download failed: {response.status_code} {file_url}')
        return False


class Session:
    requests_session_instance = requests.session()
    status = NOT_LOGGED_IN
    team_id = ''
    is_staff = False

    def request(self, method: str, url: str, params=None, data=None, files=None):
        if self.status != LOGGED_IN:
            warnings.warn('Not logged in, please login first')
            exit(1)
        if self.is_staff:
            url = url.replace('/teams', '')
        return self.requests_session_instance.request(method=method, url=url, params=params, data=data, files=files)

    def request_team_id(self):
        response = self.requests_session_instance.request('GET', 'https://api.igem.org/v1/teams/memberships/mine',
                                                          params={"onlyAcceptedTeams": True})
        team_list = response.json()
        team_list = [team for team in team_list if
                     (team['team']['status'] == 'accepted' and team['membership']['status'] == 'accepted')]
        if len(team_list) == 0:
            warnings.warn('Not joined any team')
            exit(1)
        main_team = team_list[0]['team']
        main_membership = team_list[0]['membership']
        team_id = main_team['id']
        team_name = main_team['name']
        team_year = main_team['year']
        team_role = main_membership['role']
        print('Your team:', team_id, team_name, team_year)
        print('Your role:', team_role)
        return team_id

    def login(self, username: str, password: str):
        """
        login to igem.org
        :param username: your username
        :param password: your password
        """
        data = {
            "identifier": username,
            "password": password
        }
        response = self.requests_session_instance.post('https://api.igem.org/v1/auth/sign-in', data=data)
        if response.text.__contains__('Invalid credentials'):
            self.status = LOGGED_FAILED
            warnings.warn('Invalid credentials')
            exit(1)
        else:
            self.status = LOGGED_IN

            resp = self.requests_session_instance.get('https://api.igem.org/v1/auth/me')
            user_info = resp.json()
            if 'can-manage-staff-uploads' in user_info['privileges']:
                self.is_staff = True
                resp = self.requests_session_instance.get('https://api.igem.org/v1/websites/me')
                websites_list = resp.json()['repositories']
                print('Your websites:')
                for index, website in enumerate(websites_list):
                    print((index + 1), website['path'])
                print('Please input the websites_id you want to operate:')
                while True:
                    try:
                        user_in = int(input())
                        if user_in in range(1, len(websites_list) + 1):
                            self.team_id = websites_list[user_in - 1]['path']
                            break
                        else:
                            print('Invalid websites_id, please input again:')
                    except ValueError:
                        print('Invalid input, please input again:')
                return
            self.team_id = self.request_team_id()

    def staff_login(self, username: str, password: str, website: str = ''):
        """
        login to igem.org as staff
        :param username: your username
        :param password: your password
        :param website: website you want to operate
        """
        if not website:
            warnings.warn('Please specify a website to operate')
            exit(1)
        data = {
            "identifier": username,
            "password": password
        }
        response = self.requests_session_instance.post('https://api.igem.org/v1/auth/sign-in', data=data)
        if response.text.__contains__('Invalid credentials'):
            self.status = LOGGED_FAILED
            warnings.warn('Invalid credentials')
            exit(1)
        else:
            self.status = LOGGED_IN
            self.team_id = f'websites/{website}'
            self.is_staff = True

    def change_website(self, website: str = ''):
        """
        change the website you want to operate
        :param website: website you want to operate
        """
        if not website:
            warnings.warn('Please specify a website to operate')
            exit(1)
        self.team_id = f'websites/{website}'

    def query(self, directory: str = '', output: bool = True):
        """
        query a files/dirs in specific directory
        :param directory: (optional) directory to query, default to root directory
        :param output: (optional) need to print query result, default to True
        :return: list of files, each file/dir as a dict
        """
        check_parameter(directory)
        response = self.request('GET', f'https://api.igem.org/v1/websites/teams/{self.team_id}',
                                params={'directory': directory} if directory != '' else None)
        res = response.json()
        if res['KeyCount'] > 0:
            if output:
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
                    table.add_row(['Folder', item['Name'], item['Key'].split(f'teams/{self.team_id}/')[-1]])
                else:
                    table.add_row(['File-' + item['Type'], item['Name'], item['Location']])
            if output:
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
        files = {
            'file': (path_to_file.name, open(abs_file_path, 'rb'), mime_type)
        }
        res = self.request('POST', f'https://api.igem.org/v1/websites/teams/{self.team_id}',
                           params={'directory': directory} if directory != '' else None,
                           files=files)
        if res.status_code == 201:
            print(path_to_file.name, 'uploaded', res.text)
            print()
            if list_files:
                self.query(directory)
            return res.text
        else:
            warnings.warn('Upload failed' + res.text)

    def upload_dir(self, local_abs_path: str, directory: str = ''):
        """
        upload a directory and its subdirectories to specific directory
        :param local_abs_path: absolute path of directory
        :param directory: (optional) target directory, default to root directory
        :return: list of files, each file/dir as a dict
        """
        check_parameter(directory)
        if directory == '/':
            warnings.warn('You specified \'/\' as a directory name, which may cause unknown errors')
            exit(1)
        path_to_dir = Path(local_abs_path)
        if not path_to_dir.is_dir():
            warnings.warn('Invalid directory path: ' + local_abs_path)
            exit(1)
        file_list = os.listdir(local_abs_path)
        if directory == '':
            dir_path = path_to_dir.name
        else:
            dir_path = directory + '/' + path_to_dir.name
        # multi-threading operating
        threads = []
        for filename in file_list:
            if filename.startswith('.'):
                continue
            if (path_to_dir / filename).is_file():
                thread = threading.Thread(target=self.upload,
                                          args=(f'{path_to_dir}/{filename}', dir_path, False))
                thread.start()
                threads.append(thread)
            if (path_to_dir / filename).is_dir():
                thread = threading.Thread(target=self.upload_dir,
                                          args=(f'{path_to_dir}/{filename}', dir_path))
                thread.start()
                threads.append(thread)
        for thread in threads:
            thread.join()
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
                           f'https://api.igem.org/v1/websites/teams/{self.team_id}/{filename}',
                           params={'directory': directory} if directory != '' else None)
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
        if directory == '':
            warnings.warn('Trying to truncate the root directory! Please specify a directory name instead.')
            exit(1)
        contents = self.query(directory)
        for item in contents:
            if item['Type'] == 'Folder':
                self.truncate_dir(directory + '/' + item['Name'])
            else:
                self.delete(item['Name'], directory, False)
        return self.query(directory)

    def download_dir(self, directory: str = '', files_only: bool = True):
        """
        download a directory and its subdirectories to local
        :param directory: directory to download
        :param files_only: whether to download files only, default to True
        :return: None
        """
        contents = self.query(directory, False)
        if len(contents) == 0:
            print(f'Directory {directory} is empty')
            return
        else:
            local_target_directory = f'teams/{self.team_id}/{directory}'
            if self.is_staff:
                local_target_directory = f'{self.team_id}/{directory}'
            os.makedirs(local_target_directory, exist_ok=True)
        # multi-threading operating
        threads = []
        for item in contents:
            if item['Type'] == 'Folder':
                if files_only:
                    continue
                if self.is_staff:
                    self.download_dir(item['Prefix'].split(f'{self.team_id}/')[1], files_only)
                else:
                    self.download_dir(item['Prefix'].split(f'teams/{self.team_id}/')[1], files_only)
            thread = threading.Thread(target=download_single_file,
                                      args=(item['Location'], local_target_directory))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        directory = directory if directory != '' else '/'
        print(f'Download {len(threads)} files in {directory}\n')
