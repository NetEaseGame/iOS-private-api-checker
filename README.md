## iOS私有API检查工具 ##

参考

 - [RuntimeBrowser](https://github.com/nst/RuntimeBrowser/tree/master/tools/ios_headers_history)

 - [iOS-private-api-scanner](https://github.com/mrmign/iOS-private-api-scanner)

1. `私有的api ＝ (class-dump Framework下的库生成的头文件中的api - (Framework下的头文件里的api = 有文档的api + 没有文档的api)) + PrivateFramework下的api`。
2. 私有的api在公开的Framework及私有的PrivateFramework都有。