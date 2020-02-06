# -*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.ui as ui
import requests
from sys import version_info
import time
import json
import io
import os
import re
import win32process

#是否每日评论
daily_comment=True
#是否每日打榜
daily_vote=True
#是否每日签到
daily_sign=True

#每日评论次数，5次得9经验+10积分，8次得9经验+16积分
comment_count_max=8
#失败最大尝试次数
retry_count_max=8
#每日签到，签几轮
daily_sign_count=3

chrome_process=None
chrome_path="C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
chrome_path_x64="C:/Program Files/Google/Chrome/Application/chrome.exe"
filename_chaohua= "chaohua.json"
cookie_keys_to_save = ["ALF", "SUBP", "SUB", "SSOLoginState", "SUHB"]

#每日打榜的超话,必须是手机版链接
url_super_index_vote="https://m.weibo.cn/p/1008082a98366b6a3546bd16e9da0571e34b84/super_index"
xpath_button="//*[@id=\"Pl_Core_StuffHeader__1\"]/div/div[2]/div/div[3]/div/div[3]/a"
xpath_tab="//*[@id=\"app\"]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div/div/ul/li[1]/span"
xpath_vote="//*[@id=\"app\"]/div[1]/div[1]/div[3]/div/div/div[1]/div/div/div/div[3]/div"
xpath_score="//*[@id=\"app\"]/div/div[1]/div/ul[1]/li[1]"
xpath_gift="//*[@id=\"app\"]/div/div[2]/div[2]/span[2]"
xpath_score_count="//*[@id=\"app\"]/div/div[2]/div[1]/span"

#每日五次评论的微博,必须是手机版链接
url_weibo_comment_daily="https://m.weibo.cn/status/GCR2P5U0X"
xpath_comment_box="//*[@id=\"app\"]/div[1]/div/div[5]/div/div[1]"
xpath_textarea="//*[@id=\"app\"]/div[1]/div/div[5]/div/div/div/div[1]/textarea[1]"
xpath_button_send="//*[@id=\"app\"]/div[1]/div/div[5]/div/div/div/div[2]/button"

def launch_chrome():
    global chrome
    path_exec=None
    if os.path.exists(chrome_path):
        path_exec =chrome_path
    elif os.path.exists(chrome_path_x64):
        path_exec = chrome_path_x64
    else:
        print(u"未找到Chrome安装目录")
        exit(-1)
    chrome=win32process.CreateProcess(None,"{} --remote-debugging-port=9222 ".format(path_exec),None,None,0,0,None,None,win32process.STARTUPINFO())

def get_chaohua_list(cookie, sinceId):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100803_-_page_my_follow_super"
    if sinceId != '':
        url = url + "&since_id=%s" % sinceId
    headers = {
        'Cookie': cookie
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    response = response.json()
    return response

def resolve(card_group):
    chaohua_list = []
    for card in card_group:
        if card['card_type'] == 8:
            scheme = card['scheme']
            if version_info.major == 2:
                import urlparse
                query = urlparse.urlparse(scheme).query
            else:
                from urllib.parse import urlparse
                query = urlparse(scheme).query
            parmsList = query.split('&')
            containerid = ''
            for parm in parmsList:
                r = parm.split('=')
                if r[0] == 'containerid':
                    containerid = r[1]
                    break
            chaohua = {
                'title_sub': card['title_sub'].encode("utf-8"),
                'containerid': containerid
            }
            chaohua_list.append(chaohua)
    return chaohua_list

def main():
    #启动本机的Chrome,需要提前登录上微博账号
    launch_chrome()
    chrome_options = Options()
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    error_count = 1
    wait = ui.WebDriverWait(driver, 10)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    #每日评论多次
    if daily_comment:
        driver.get(url_weibo_comment_daily)
        comment_count=1
        while True:
            try:
                wait.until(lambda driver: driver.find_element_by_xpath(xpath_comment_box).is_displayed())
                comment_box=driver.find_element_by_xpath(xpath_comment_box)
                comment_box.click()
                wait.until(lambda driver: driver.find_element_by_xpath(xpath_textarea).is_displayed())
                textarea=driver.find_element_by_xpath(xpath_textarea)
                comment=u"每日评论，第{}次".format(comment_count)
                textarea.send_keys(comment)
                print(comment)
                button_send=driver.find_element_by_xpath(xpath_button_send)
                button_send.click()
                time.sleep(5)
                comment_count+=1
                if comment_count>comment_count_max:
                    break
            except:
                driver.refresh()
                error_count += 1
                if error_count>retry_count_max:
                    error_count = 1
                    break

    # 每日超话打榜
    if daily_vote:
        #第一步，找到“打榜按钮”，点击进入打榜页面
        driver.get(url_super_index_vote)
        while True:
            if error_count > retry_count_max:
                error_count = 1
                break
            try:
                print(u"登入主页")
                wait.until(lambda driver: driver.find_element_by_xpath(xpath_tab).is_displayed())
                tab=driver.find_element_by_xpath(xpath_tab)
                print(u"点击帖子")
                tab.click()
                wait.until(lambda driver: driver.find_element_by_xpath(xpath_vote).is_displayed())
                button_vote=driver.find_element_by_xpath(xpath_vote)
                print(u"点击打榜")
                button_vote.click()
                wait.until(lambda driver: driver.find_element_by_xpath(xpath_score).is_displayed())
                break
            except:
                print(u"刷新，第{}次".format(error_count))
                driver.refresh()
                error_count += 1

        #第二步，选择1积分
        while True:
            if error_count > retry_count_max:
                error_count = 1
                break
            print(u"选择1积分")
            button_score=driver.find_element_by_xpath(xpath_score)
            if button_score.get_attribute("class")=="active":
                break
            button_score.click()
            time.sleep(3)
            error_count += 1

        #第三步，点击“赠送”按钮，判断打榜是否成功、是否出现行为检测异常
        score_before=driver.find_element_by_xpath(xpath_score_count)
        score_before=score_before.text
        score_before=re.findall(u"(?<=我的积分：).*",score_before)
        score_before=int(score_before[0])
        while True:
            if error_count > retry_count_max:
                error_count = 1
                break
            try:
                button_gift = driver.find_element_by_xpath(xpath_gift)
                print(u"送积分")
                button_gift.click()
                time.sleep(3)
                score_now=driver.find_element_by_xpath(xpath_score_count)
                score_now=score_now.text
                score_now=re.findall(u"(?<=我的积分：).*",score_now)
                score_now=int(score_now[0])
                if score_now<score_before:
                    break
                else:
                    print(u"送积分未成功")
                    error_count +=1
            except NoSuchElementException:
                print(u"检测异常")
                break

    # 每日超话签到
    if daily_sign:
        for i in range(daily_sign_count):#签n轮
            #第一步,获取超话列表
            if os.path.exists(filename_chaohua):
                chaohua_list =json.loads(open(filename_chaohua).read())
            else:
                chaohua_list = []
                # 从浏览器获取cookie
                driver.get(url_super_index_vote)
                cookies = driver.get_cookies()
                cookie_temp = ""
                for item in cookies:
                    if item["name"] in cookie_keys_to_save:
                        cookie_temp += "{}={};".format(item["name"], item["value"])
                since_id = ""
                un_terminal = True
                while un_terminal:
                    response_json = get_chaohua_list(cookie_temp, since_id)
                    cardlist_info = response_json['data']['cardlistInfo']
                    card_group =[]
                    for group in response_json['data']['cards']:
                        group_name=group["card_type_name"]
                        if group_name=="my_topic_follow_super" or group_name=="my_topic_manage_super":
                            card_group += group['card_group']
                    chaohua_list = chaohua_list + resolve(card_group)
                    if 'since_id' in cardlist_info:
                        since_id = cardlist_info['since_id']
                    else:
                        print(u"获取超级话题列表结束...准备开始签到")
                        break
                with io.open(filename_chaohua, "w", encoding="utf-8") as fd:
                    text=json.dumps(chaohua_list, indent=4)
                    if type(text) == str:
                        text = text.decode("utf-8")
                    fd.write(text)

            #每个超话都签到
            for item in chaohua_list:
                print("-------------------")
                print(u"准备签到{}" .format(item['title_sub']))
                button_sign=None
                text =""
                while True:
                    if error_count > retry_count_max:
                        error_count = 1
                        break
                    try:
                        driver.get("https://weibo.com/p/{}/super_index".format(item['containerid']))
                        time.sleep(5)
                        button_sign = driver.find_element_by_xpath(xpath_button)
                        text = button_sign.text
                        break
                    except NoSuchElementException:
                        driver.refresh()
                        time.sleep(10)
                        error_count += 1
                if text == u"已签到" or text == "" or button_sign==None:
                    print(u"跳过{}".format(item['title_sub']))
                    continue
                while True:
                    if error_count > retry_count_max:
                        error_count = 1
                        break
                    try:
                        print(u"点击")
                        button_sign.click()
                        time.sleep(3)
                        button_sign = driver.find_element_by_xpath(xpath_button)
                        text = button_sign.text
                        if text == u"已签到":
                            print(u"点击成功")
                            break
                        else:
                            print(u"签到未成功")
                            error_count += 1
                    except:
                        print(u"签到异常")
                        try:
                            alert = driver.find_element_by_class_name("W_layer_btn")
                            if alert:
                                if u"解除异常" in alert.text:
                                    print(u"签到出现异常")
                                    break
                        except NoSuchElementException:
                            pass
                        error_count += 1
                time.sleep(3)
                print("-------------------")
            print("-------------------")

    # 关闭浏览器进程
    try:
        driver.quit()
        win32process.TerminateProcess(chrome[0], 0)
    except:
        pass
    #关闭残留进程
    try:
        os.system("taskkill /IM chromedriver.exe /F")
        os.system("taskkill /IM chrome.exe /F")
    except:
        pass

if __name__=="__main__":
    main()
