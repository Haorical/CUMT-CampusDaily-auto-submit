# CUMT-CampusDaily-auto-submit
适用于中国矿业大学晨午检自动打卡，妈妈再也不用担心我忘记打卡了
@[TOC](CUMT今日校园晨午检自动打卡)

>寒假就有这个打算了，但在家太懒了，懒得弄，在学校上网课太无聊了，就基于子墨大佬的[Github项目](https://github.com/ZimoLoveShuang/auto-submit)改了改，用了一天终于搞完了，弄成了矿大专属的，现在对矿大的学生来说是傻瓜式操作了。

# 项目地址
```c
https://github.com/Haorical/CUMT-CampusDaily-auto-submit
```

# 最终成品
![](https://img-blog.csdnimg.cn/20210310174220497.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzUwMDM4MjEx,size_16,color_FFFFFF,t_70)


# 使用方法
1.  git克隆代码到本地，有用的是下面3个文件
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210310174431200.png)
其中config.yml是配置文件，也就是需要改的；
index.py是运行文件，不用管;
requirements.txt是依赖文件;

2. 安装依赖环境，pip命令安装
```c
pip install -r requirements.txt
```
3. 更改config里面的设置，学号和密码
![在这里插入图片描述](https://img-blog.csdnimg.cn/2021031017573045.png)
4. config设置里面一开始的api,由于是我自己的服务器，就不分享了，可以选择自己搭建，[点这里](https://blog.zimo.wiki/posts/6c809f81/)，教程挺详细的。还有server酱如果你需要的话，百度就行。
5. 到现在为止就ok了，运行index.py就能实现打卡。但我们需要的是实现自动打卡，实现自动打卡有好多方式：windows计划任务或者腾讯云函数比较常见，当然有服务器的话直接挂服务器上就行。
[windows计划任务设置](https://jingyan.baidu.com/article/154b463130041128ca8f41c7.html)
**腾讯云函数：**
1.打开百度搜索腾讯云函数，注册认证后，进入控制台，点击左边的层，然后点新建，名称随意，然后点击上传zip，选择release中的dependency.zip上传，然后选择运行环境python3.6，然后点击确定，耐心等待一下，上传依赖包需要花费的时间比较长 
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210310181911184.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzUwMDM4MjEx,size_16,color_FFFFFF,t_70)

	2.新建腾讯云函数依赖点左边的函数服务，新建云函数，名称随意，运行环境选择python3.6，创建方式选择空白函数，然后点击下一步 新建腾讯云函数
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210310182002675.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzUwMDM4MjEx,size_16,color_FFFFFF,t_70)

	3.提交方法选择在线编辑，把本地修改好的index.py直接全文复制粘贴到云函数的index.py，然后点击文件->新建，文件名命名为config.yml，然后把本地配置好的config.yml文件中的内容直接全文复制粘贴到云函数的config.yml文件，点击下面的高级设置，设置超时时间为60秒，添加层为刚刚新建的函数依赖层，然后点击完成

	![在这里插入图片描述](https://img-blog.csdnimg.cn/20210310182013762.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L20wXzUwMDM4MjEx,size_16,color_FFFFFF,t_70)
	4.配置腾讯云函数
	进入新建好的云函数，左边点击触发管理，点击创建触发器，名称随意，触发周期选择自定义，然后配置cron表达式，下面的表达式表示每天中午十二点整执行
0 0 12 * * * *
	5.然后就可以测试云函数了，绿色代表云函数执行成功，红色代表云函数执行失败（失败的原因大部分是由于依赖造成的）。返回结果是success.，代表自动提交成功，如遇到问题，请仔细查看日志
	>这是子墨写的，我直接挂在服务器上了，没这么麻烦

# 遇到的BUG

 - 因为子墨很久没更新了，今日校园升级了接口，直接打开项目，会报错，我直接在index.py里把学校默认成矿大了，就不需要调用了
 - 子墨提供的今日校园模拟登录的api貌似不能用，我根据他另一个项目自己搭建了一个
 - 显示提交错误，这个是因为今日校园des更换密钥了。
 - 去除了一些无关的代码，比如图像上传什么的，不需要

# 联系我
**本项目仅供学习交流使用，如作他用所承受的任何直接、间接法律责任一概与作者无关**
**如果此项目侵犯了您或者您公司的权益，请立即联系我删除**

如果你有不懂的,或者需要api不会搭建的,欢迎联系我,我会看心情给你解答（狗头）
>qq：2507582949
