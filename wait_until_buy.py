#python3.6.5
#coding:utf-8
'''
@time:2020-02-18
@author: maodou38
仅作为学习过程中的实践，无商业用途
'''
import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import time
import random

#邮件发送
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# 第三方 SMTP 服务
my_sender='rio_maodou@sina.com'    # 发件人邮箱账号
my_pass = 'b6d5a0c923552897'       # 发件人邮箱密码

# ==== 设定抢购时间 （修改此处，指定抢购时间点）====
#BUY_TIME = "2020-02-17 19:59:58"

# ====  标识登录状态、重试次数 ====
MAX_LOGIN_RETRY_TIMES = 10

current_retry_login_times = 0
login_success = False
#buy_time_object = datetime.datetime.strptime(BUY_TIME, '%Y-%m-%d %H:%M:%S')

now_time = datetime.datetime.now()
'''if now_time > buy_time_object:
    print("当前已过抢购时间，请确认抢购时间是否填错...")
    exit(0)
'''
print("正在打开chrome浏览器...")
#让浏览器不要显示当前受自动化测试工具控制的提醒
option = webdriver.ChromeOptions()
option.add_argument('disable-infobars')
driver = webdriver.Chrome(chrome_options=option)
driver.maximize_window()
print("chrome浏览器已经打开...")


def __login_operates():
    driver.get("https://www.taobao.com")
    try:
        if driver.find_element_by_link_text("亲，请登录"):
            print("没登录，开始点击登录按钮...")
            driver.find_element_by_link_text("亲，请登录").click()
            print("请使用手机淘宝扫描屏幕上的二维码进行登录...")
            time.sleep(10)
    except:
        print("已登录，开始执行跳转...")
        global login_success
        global current_retry_login_times
        login_success = True
        current_retry_login_times = 0

def login():
    print("开始尝试登录...")
    __login_operates()
    global current_retry_login_times
    while current_retry_login_times < MAX_LOGIN_RETRY_TIMES:
        current_retry_login_times = current_retry_login_times + 1
        print("当前尝试登录次数：" + str(current_retry_login_times))
        __login_operates()
        if login_success:
            print("登录成功")
            break;
        else:
            print("等待登录中...")
    if not login_success:
        print("规定时间内没有扫码登录淘宝成功，执行失败，退出脚本!!!")
        exit(0);
        time.sleep(3)
    now = datetime.datetime.now()
    print('login success:', now.strftime('%Y-%m-%d %H:%M:%S'))

def buy(url,to_send):
    #打开购物车
    driver.get(url)
    time.sleep(2)
    flag=True
    #确定该页面商品是否失效
    while flag:
        try:
            if driver.find_element_by_class_name("sold-out-left"):
                print("页面商品失效，准备刷新页面重试")
                time.sleep(10)
                driver.get(url)
        except:
            print("页面有效，开始购买")
            try:
                if driver.find_element_by_class_name("J_TSaleProp"):
                    print("找到商品选择标签")
                    driver.find_element_by_css_selector(".J_TSaleProp > li:first-child > a").click()#选中首个商品并点击
                    print("选中商品")
                    flag=False
                    driver.find_element_by_id("J_LinkBuy").click() #点击立即购买
                    #等待页面跳转
                    has_jump=False
                    while not has_jump:
                        try:
                            if driver.find_element_by_link_text("提交订单"):
                               has_jump=True
                               driver.find_element_by_link_text("提交订单").click()
                        except:
                            time.sleep(0.2)
                    #未完待续   邮件通知
                    i=1
                    while i<10 :
                       ret=mail(to_send)
                       i=i+1
                       if(ret):
                           print("邮件发送成功")
                           break
            except:
                pass
def mail(to_send):
    ret=True
    try:
        msg=MIMEText('提交订单成功，请尽快购买','plain','utf-8')
        msg['From']=formataddr(["rio_maodou",my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To']=formataddr(["dear",to_send]) # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject']="提交订单成功，请尽快购买"                # 邮件的主题，也可以说是标题
        server=smtplib.SMTP_SSL("smtp.sina.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender,[to_send,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret=False
    return ret
if __name__=="__main__":
   url=input("请输入商品链接:")
   to_send=input("请输入通知邮箱:")
   login()
   buy(url,to_send)