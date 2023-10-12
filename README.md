# igem-uploads

## Background

`Team Wiki` has long been a characteristic hallmark of iGEMers. By vividly illustrating and eloquently describing their
projects from various angles on accessible websites, all teams can monitor progress and draw inspiration from others.
This fosters inter-team collaborations and strengthens connections within the iGEM community. Year after
year, `Team Wiki` has become the most standardized and prevalent portal for teams' projects, delighting people
worldwide.

In 2022, iGEM took an innovative step by integrating GitLab, a powerful project management platform. This integration
streamlined the project building and release process, but challenges persist in building and maintaining the team wiki.

During the building process, team members frequently commit changes to their IDE (Integrated Development Environment).
When these commits impact references to picture resources, team members must also navigate web browsers to add or modify
files hosted on _[uploads.igem.org](https://uploads.igem.org)_, in accordance with the policy. This necessitates
frequent
switching between the browser and their IDE. Moreover, the heavy traffic often strains the network, increasing the risk
of the server becoming unreachable.

## Description

Our primary aim is to simplify the process for iGEMers when it comes to committing images, reducing the need for
constant switching between web browsers and their IDEs. We aspire to provide a more convenient way to access and upload
content, allowing wiki builders to focus on creating and designing webpages within their IDE with fewer distractions.

We also aim to enhance the overall user experience with our content hosting site. We will offer a means to access their
remote directory without requiring the use of a web browser, thereby reducing the graphical and unrelated content
requests and relieving the load on the _[uploads.igem.org](https://uploads.igem.org)_ webpage.

In addition, the software must be user-friendly, as we intend to make it easier for all iGEMers to upload their wiki
assets, enhance their project illustrations, and better express themselves. It will be designed as cross-platform
software, ensuring that wiki builders can deploy it on any operating system, collaborate effectively, and keep their
projects on track.

## Technical Information

After analyzing the requirements and expectations, we have conceived the idea of developing a console software that is
easy to set up and ready to use out-of-the-box. This program will be seamlessly integrated into the console, enabling
iGEMers to operate it by simply entering commands within their IDE or system terminal, just a click away.

Python serves as the foundation for our project. Python is a versatile, cross-platform programming language with
extensive support libraries and a large, active community base. This choice allows us to quickly prototype and develop
our software effectively.

To interact with users, we employ the `warnings` module to send informative messages to the terminal, and `prettytable`
to format structural data. We import the `requests` library to send requests and retrieve data from websites, and
use `etree` to parse HTML information. For streamlined file location, we have also incorporated the `path` module.

Thanks to these powerful Python libraries, we have successfully developed this versatile tool.

## Installation

Our software can be easily installed using pypi:

```shell
python3 -m pip install igem-uploads
```

## Usage

### 0. Initial configuration

Log in to _igem.org_ with your username and password registered on the official site.

```python
client = uploads.Session()
client.login('username', 'password')
```

### 1. Upload single file to specific directory

You can upload a file in a specified local directory to a remote directory. Files will be upload to remote root if you
omit the _target_directory_ argument.

```python
client.upload('path/to/file')
client.upload('path/to/file', 'target_directory')
```

### 2. Query files/directories in specific directory

To list all files and directories in a directory, simply type the command below. The software will list all items in
root directory if _directory_ is omitted.

```python
client.query('')
client.query('directory')
```

### 3. Upload directory to specific directory

If you want to upload a directory and its subdirectories to specific directory, you can use _upload_dir_. All items in
the dir you specified will be upload to remote root is _target_directory_ is omitted.

```python
client.upload_dir('path/to/directory')
client.upload_dir('path/to/directory', 'target_directory')
```

### 4. Delete single file in specific directory

To delete a specific file, call _delete_ with your filename specified.

```python
client.delete('filename', 'file_parent_directory')
```

### 5. Truncate directory

To truncate a directory, call _truncate_ and specify it.

```python
client.truncate_dir('target_directory')
```

## Conclusion

Through promotion through multiple channels (Slack, Twitter, China iGEMer Community, etc.), our software has been
downloaded and used many times. See this [link](https://pypistats.org/packages/igem-uploads).

![](https://static.igem.wiki/teams/4687/wiki/content-pages/software/04-software.png)
![](https://static.igem.wiki/teams/4687/wiki/content-pages/software/05-software.png)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors and acknowledgment

- [Tianyi LIANG](https://github.com/lty2002) - Building and publishing
- [Yi HAN](https://github.com/jacobavalanchel) - Testing and documentation

## Links

- [PyPI](https://pypi.org/project/igem-uploads/)
- [GitHub](https://github.com/iGEM-HBUT-China/igem-uploads)
- [GitLab](https://gitlab.igem.org/2023/software-tools/hbut-china)
