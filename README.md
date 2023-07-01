# igem-uploads

**igem-uploads** helps iGEMers upload their files to the iGEM server.

## Installation

```shell
pip install igem-uploads
```

## Usage

```python
import uploads

# create a session instance, login to igem.org
client = uploads.Session()
client.login('username', 'password')

# upload a file to specific directory
client.upload('path/to/file', 'target_directory')

# query files/dirs in specific directory
client.query('target_directory')

# upload a directory and its subdirectories to specific directory
client.upload_dir('path/to/directory', 'target_directory')

# delete file in specific directory
client.delete('filename', 'file_parent_directory')

# truncate a directory
client.truncate_dir('directory')
```

## Links

- [PyPI](https://pypi.org/project/igem-uploads/)
- [GitLab](https://gitlab.igem.org/2023/software-tools/hbut-china)
