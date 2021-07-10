<img src='static/img/logo.png' width='400' title='MeowFile, A file management system'>

A file sharing management system by [Topaz](https://topaz1618.github.io/about)|[Website](http://topazaws.com/)|[Blog](https://topaz1618.github.io/blog/)

[英文 README](https://github.com/Topaz1618/FileManageSystem/blob/master/README.md)


# Features:
    - 用户登录/登出，密码重置，权限管理
    - 文件上传(支持断点上传，批量上传)
    - 文件下载
    - 批量管理文件
    - 待审核文件提醒
    - 用户下载记录查看


# Environment
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

## 【上传文件】
<img src='static/images/upload.gif' title='MeowFile, A file management system'>

## 【下载文件】
<img src='static/images/download1.gif' title='MeowFile, A file management system'>

## 【用户列表】
<img src='static/images/user_list.png' width='800' title='MeowFile, A file management system'>

## 【查看下载日志】
<img src='static/images/log.gif' title='MeowFile, A file management system'>


## 【创建用户】
<img src='static/images/create_user.gif' title='MeowFile, A file management system'>

## 【其它页面】
Not logged in or access the wrong path）
<img src='static/images/others.gif' title='MeowFile, A file management system'>

## GIF 生成命令
```
    ffmpeg -i test.mp4 -s 1920x1080 -r 10 -vf scale=800:450 output.gif //  -r: specify frame rate
```
[查看更多 ffmpeg](https://topaz1618.github.io/about)


[Topaz](https://topaz1618.github.io/about)|[Website](http://topazaws.com/)|[Blog](https://topaz1618.github.io/blog/)

## License
Licensed under the MIT license