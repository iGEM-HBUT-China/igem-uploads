# igem-uploads

**igem-uploads** helps iGEMers upload their files to the iGEM server.

## Installation

```shell
pip install igem-uploads
```

## Usage

```python
import uploads

# create a session instance
client = uploads.Session()
# login to igem.org
client.login('username', 'password')

# upload a file to specific directory
client.upload('path/to/file')
client.upload('path/to/file', 'target_directory')

# query files/dirs in specific directory
client.query('')
client.query('directory')

# upload a directory and its subdirectories to specific directory
client.upload_dir('path/to/directory')
client.upload_dir('path/to/directory', 'target_directory')

# delete file in specific directory
client.delete('filename', 'file_parent_directory')

# truncate a directory
client.truncate_dir('target_directory')
```

## Links

- [PyPI](https://pypi.org/project/igem-uploads/)
- [GitHub](https://github.com/iGEM-HBUT-China/igem-uploads)
- [GitLab](https://gitlab.igem.org/2023/software-tools/hbut-china)
