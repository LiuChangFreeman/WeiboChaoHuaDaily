微博超话每日经验22点全收集脚本
![](http://static.aikatsucn.cn/images/weibo-chaohua-daily/5.jpg)
# 适用条件
1 Windows 7及以上

2 Python 2.7-3.7

3 已安装Chrome浏览器

# 使用方法
0 安装Python、Chrome、requirements.txt中的库，以及放置chromedriver.exe到环境变量Path中

1 在Chrome上登录您的微博账号

![1](http://static.aikatsucn.cn/images/weibo-chaohua-daily/1.png)

2 修改您需要打榜的超话链接(每日打榜8点经验)

```
#每日打榜的超话链接,必须是手机版
url_super_index_vote="https://m.weibo.cn/p/1008082a98366b6a3546bd16e9da0571e34b84/super_index"
```
![2](http://static.aikatsucn.cn/images/weibo-chaohua-daily/2.png)
3 修改您需要每日互动的微博链接(每日评论5条，6点经验)

```
#每日五次评论的微博链接,必须是手机版
url_weibo_comment_daily="https://m.weibo.cn/status/GCR2P5U0X"
```
![3](http://static.aikatsucn.cn/images/weibo-chaohua-daily/3.png)

4 创建Windows每日计划任务
![4](http://static.aikatsucn.cn/images/weibo-chaohua-daily/4.png)