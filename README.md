<img src='static/images/meowfile.png' width='400' title='MeowFile, A file management system'>

A file sharing management system by [Topaz](https://topaz1618.github.io/about)|[Website](http://topazaws.com/)|[Blog](https://topaz1618.github.io/blog/)

[Chinese README](https://github.com/Topaz1618/FileManageSystem/blob/master/README_CN.md)


## Features:
- User login/logout, password reset, authority management
- File upload (support breakpoint upload, batch upload)
- file download
- Batch management of files
- Document review process(Only for users with intranet permissions)

## Environment
- Python3
- Tornado
- Ubuntu16.04/ Mac OS
- Mysql

## Requirements
- tornado >= 6.1
- PyJWT == 1.7.1

## Installation (Ubuntu & Mac OS)
1. Download MeowFile
```
    $ git clone git@github.com:Topaz1618/MeowFile.git
```

2. Install dependencies
```
    pip install -r requirements.txt
```

3. Create database & Generate admin user
```
    python models.py
```

4. Modify configuration
```
    $ cd MeowFile
    $ vim config.py
    USERNAME = "root"
    PASSWORD = "123456"
    HOST = "127.0.0.1"
    PORT = "3306"
    DATABASE = "ManageFileDB"
```


## Run
```
    python apps.py
```

## Screenshots

## 【Upload File】
<img src='static/images/upload.gif' title='MeowFile, A file management system'>

## 【Download File】
<img src='static/images/download1.gif' title='MeowFile, A file management system'>

## 【User List Page】
<img src='static/images/user_list.png' width='800' title='MeowFile, A file management system'>

## 【Manage User Permissions】
<img src='static/images/user_management.gif'   title='MeowFile, A file management system'>

## 【Create User】
<img src='static/images/create_user.gif' title='MeowFile, A file management system'>

## 【Other Pages】
（Not logged in or access the wrong path）
<img src='static/images/others.gif' title='MeowFile, A file management system'>

## GIF production command
```
    ffmpeg -i test.mp4 -s 1920x1080 -r 10 -vf scale=800:450 output.gif //  -r: specify frame rate
```

## License
Licensed under the MIT license