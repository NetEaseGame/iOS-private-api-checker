## iOS私有API检查工具 ##


### 一、如何使用 ###

#### 1. 构建私有api库 ####

 - db/dsidx_dbs.py文件为解析docSet.dsidx的库，请实现将docSet.dsidx内容导出到sqlite中。docSet.dsidx是xcode作为代码提示的数据库，表示是apple公开的公有api。

 - 修改config.py中sdks_config字典，增加各个version的sdk路径，然后运行build_api_db.py，会自动解析私有api，存存储到sqlite中。

 - (项目中的数据库内容是我编译sdk7.0的数据，可以直接用。)


#### 2. 检查ipa私有api ####

运行方式有二，建议第二种web方式：

1. 修改iOS_private.py main方法中的ipa路径，运行即可。

2. 使用Web上传运行的方式，运行python run_web.py（请先配置flask运行环境），然后浏览器输入127.0.0.1:9527 将ipa拖入上传框等待即可看到检查结果。

![web_screenshot](screenshot/web_screenshot.png)


### 二、参考项目 ###

 - [RuntimeBrowser](https://github.com/nst/RuntimeBrowser/tree/master/tools/ios_headers_history)
 - [iOS-private-api-scanner](https://github.com/mrmign/iOS-private-api-scanner)
 - [iOS-api-scan.md](iOS-api-scan.md)


### 三、Note ###

1. `私有的api ＝ (class-dump Framework下的库生成的头文件中的api - (Framework下的头文件里的api = 有文档的api + 没有文档的api)) + PrivateFramework下的api`。
2. 私有api在公开的Framework及私有的PrivateFramework都有。
3. 请暂时暂mac上运行，linux上暂时没有找到合适的、代替otool的工具，求推荐^^!