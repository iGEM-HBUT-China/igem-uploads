import mimetypes
import os
import warnings

import requests
from lxml import etree

NOT_LOGGED_IN = 0
LOGGED_IN = 1
LOGGED_FAILED = -1


class Session:
    requests_session_instance = requests.session()
    status = NOT_LOGGED_IN
    team_id = ''

    def request(self, method, url, data=None):
        if self.status != LOGGED_IN:
            warnings.warn('Not logged in, please login first')
            exit(1)
        return self.requests_session_instance.request(method=method, url=url, data=data, verify=False)

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
        print('Your team info:', team_id, team_name, team_year)
        print('Your role:', team_role)
        if team_status != 'Accepted':
            warnings.warn('Your team is not accepted')
        if team_role_status != 'Accepted':
            warnings.warn('Your team role is not accepted')
        return team_id

    def login(self, username, password):
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

    # TODO 以下代码逻辑待优化，igem接口响应数据有所改变
    def query(self, directory=''):
        """
        在指定目录下查找
        :param directory: 要查找的目录，默认为根目录
        :return: 文件的list/空list
        """
        warnings.warn("this implement is outdated", DeprecationWarning)
        data = dict(directory=directory)
        response = self.request('GET', 'https://shim-s3.igem.org/v1/teams/' + self.team_id + '/wiki', data=data)
        res = response.json()
        if res['KeyCount'] > 0:
            print(directory, '查询成功', res['KeyCount'])
            for i in res['Contents']:
                print(i['Name'], i['Location'])
            print()
            return res['Contents']
        else:
            print(directory, '查询为空')
            print()
            return []

    def upload(self, abs_file_path, directory='', list=True):
        """
        上传文件到指定目录
        :param abs_file_path: 文件的绝对路径
        :param directory: 文件的目录，默认为根目录
        :param list: 是否查询
        :return: 文件的URL/False
        """
        warnings.warn("this implement is outdated", DeprecationWarning)
        filename = abs_file_path.split('\\')[-1]
        mime_type = mimetypes.guess_type(filename, True)[0]
        data = {
            'directory': directory
        }
        files = {
            'file': (filename, open(abs_file_path, 'rb'), mime_type)
        }
        res = self.requests_session_instance. \
            request('POST', 'https://shim-s3.igem.org/v1/teams/' + self.team_id + '/wiki', data=data, files=files)
        if res.status_code == 201:
            print(filename, '上传成功', res.json()['location'])
            print()
            if list:
                self.query(directory)
            return res.json()['location']
        else:
            print(res.text)
            print(filename, '上传失败')
            print()
            return False

    def upload_dir(self, abs_path):
        """
        上传目录
        :param abs_path: 目录的绝对路径
        :return: 目录下文件的list/空list
        """
        warnings.warn("this implement is outdated", DeprecationWarning)
        file_list = os.listdir(abs_path)
        for filename in file_list:
            self.upload(abs_path + '\\' + filename, abs_path.split('\\')[-1], False)
        return self.query(abs_path.split('\\')[-1])

    def delete(self, filename, directory='', list=True):
        """
        删除某目录下的文件
        :param filename: 文件名
        :param directory: 文件的目录，默认为根目录
        :param list: 是否查询
        :return: True/False
        """
        warnings.warn("this implement is outdated", DeprecationWarning)
        data = dict(directory=directory)
        res = self.requests_session_instance. \
            request('DELETE',
                    'https://shim-s3.igem.org/v1/teams/' + self.team_id + '/wiki/' + filename, data=data)
        if res.status_code == 200:
            print(directory + '/' + filename, '删除成功')
            print()
            if list:
                self.query(directory)
            return True
        else:
            print(directory + '/' + filename, '删除失败')
            print()
            return False

    def clear_dir(self, directory):
        """
        清空目录
        :param directory: 目录
        :return: 清空后目录下的文件
        """
        warnings.warn("this implement is outdated", DeprecationWarning)
        files = self.query(directory)
        print(files)
        for file in files:
            self.delete(file['Name'], directory, False)
        return self.query(directory)
