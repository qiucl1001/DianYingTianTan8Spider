# DianYingTianTan8Spider
## 电影天堂吧：[https://www.dytt8.net]

### 本项目抓取最新全部电影，并将每部电影相关数据信息存入MySQL数据库

备注：本项目一共有3个子项目文件
`spider.py`使用对接搭建的免费ip代理池
`spider_2.py` 使用付费三方代理商<阿布云动态隧道代理> 
`spider_3.py` 使用宿主机所在网外与免费的ip代理池对接 亲测，效果可以！


---
## 安装

### 安装Python3.7.2以上版本

### 安装MySQL数据库
安装好之后开启MySQL数据库

###安装三方依赖库

```
pip3 install -r requirements.txt
```

## 配置 DianYingTianTan8Spider
### 打开 models.py 配置mysql数据库连接
```
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://数据库用户名:数据库连接密码@数据库所在宿主机ip:3306/数据库名称'
e.g.
 SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:qcl123@127.0.0.1:3306/district_code'
 
```
### 手动创建数据库
```
mysql -u数据库用户名 -p数据库连接密码

mysql> create database district_code default charset="utf8";

```
### 创建迁移仓库
#### 这个命令会创建migrations文件夹，所有迁移文件都放在里面。
```
python database.py db init
```
### 创建迁移脚本
#### 创建自动迁移脚本
```
python database.py db migrate -m 'initial migration'
```

### 更新数据库
```
python database.py db upgrade
```

## 启动程序
```
cd dianyingtiantan8spider
python spider_3.py(spider_2.py、spider.py)
```




