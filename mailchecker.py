# coding: utf-8
import datetime
import math
import time
import json
import urllib.request  as urllib2 
import requests
import time
from time      import sleep
from selenium  import webdriver
from multiprocessing import Pool
from itertools import product
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import Proxy,ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
import os, sys
import http.client
import MySQLdb
import mysql.connector
from mysql.connector import errorcode
from numpy import random
from datetime import datetime
import traceback

TIMEOUT_SHORT=5
TIMEOUT_MEDIUM=10
TIMEOUT_LONG=20

DB_config = {
	'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'mailcheck'
}

try:
  cnx = mysql.connector.connect(**DB_config)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  print('success')

db = MySQLdb.connect(**DB_config)
DB = db.cursor()

def getProxies() :
  query = "SELECT * FROM proxies;"
  DB.execute(query)
  global Proxies, Proxies_num
  Proxies = DB.fetchall()
  Proxies_num = DB.rowcount

def getEmailAdresses() :
  query = "SELECT * FROM emailaddresses ORDER BY id;"
  DB.execute(query)
  global EmailAdresses, EmailAdresses_num
  EmailAdresses = DB.fetchall()
  EmailAdresses_num = DB.rowcount

def getBrowser() :
  query = "SELECT * FROM browser;"
  DB.execute(query)
  global Browser, Browser_num
  Browser = DB.fetchall()
  Browser_num = DB.rowcount

def getSendingDomains() :
  query = "SELECT * FROM sendingdomains;"
  DB.execute(query)
  global SendingDomains
  SendingDomains = DB.fetchall()

def getSpamDomains() :
  query = "SELECT * FROM spamdomains;"
  DB.execute(query)
  global SpamDomains
  SpamDomains = DB.fetchall()

def getResponses() :
  query = "SELECT * FROM responses;"
  DB.execute(query)
  global Responses
  Responses = DB.fetchall()

# loginArr = []
processName = {}
def work_log(mail):
  # print(mail)
  # print("loginArr : ", loginArr)
  # time.sleep(1)
  mail_address = mail[0][1].split("@")[1]
  main_address = mail_address.split(".")[0]
  print(mail)
  print(main_address)
  if main_address == "gmail" :
    url = 'https://accounts.google.com/'
  elif main_address == "yahoo" :
    url = 'https://login.yahoo.com/'
    # Ignore yahoo for now
    # return 

  browser_index = random.randint(Browser_num-1)
  browser_name = Browser[browser_index][1]
  ua = UserAgent()
  userAgent = ua.random
  userAgent = userAgent.split(" ")
  userAgent[0] = browser_name
  userAgent = " ".join(userAgent)
  userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('user-agent={0}'.format(userAgent))
  proxy_index = random.randint(Proxies_num-1)
  proxies = Proxies[proxy_index][1]
  print("Using proxy:", proxies)
  chrome_options.add_argument('--proxy-server=%s' % proxies)
  driver = webdriver.Chrome(chrome_options=chrome_options)
  try:
    # driver = webdriver.Chrome()
    driver.set_window_size(1024,900)
    # time.sleep(5)
    # loginArr[mail[1]] = logIn
    # loginArr[mail[1]](mail[0], url, driver, proxies)
    # logIn(mail, url, driver)
    processName[mail[0][0]] = logIn
    processName[mail[0][0]](mail[0], url, driver, proxies)
  except Exception as e:
    driver.save_screenshot(datetime.now().strftime("screenshot_%Y%m%d_%H%M%S_%f.png"))
    raise e

  finally:
    driver.quit()

def pool_handler() :
  # EmailAdresses = [
  #   ["1", 'DeannaMLyons528@yahoo.com', 'GHajk$a47', ''],
  #   ["1", 'janwheeler197335@gmail.com', 'aleiivrc', 'nwxdrjem']
  # ]
  work = []
  work = [(ind, {}) for ind in EmailAdresses]
  # print(EmailAdresses)
  #
  # return
  p = Pool(2)
  p.map(work_log, work)
  try :
    p.join()
  except :
    pass

def openPage() :
  if __name__ == '__main__':
    pool_handler()

      
def logIn(mail, url, driver, proxy_ip) :
  print("logging in...")
  url_check = url.find("google")
  if url_check >= 0 :
    googleLogin(mail, driver)
    gmailSpam(driver)
    gmailInbox(driver, proxy_ip)
  else :
    yahooLogin(mail, driver)
    yahooMailSpam(driver)
    yahooMailInbox(driver, proxy_ip)

def fail_with_error(message):
  def decorator(fx):
    def inner(*args, **kwargs):
      try:
        return fx(*args, **kwargs)
      except Exception as e:
        print(message)
        raise e
    return inner
  return decorator

@fail_with_error("Cannot set email address")
def google_set_login(driver, mail_address):
  try:
    email_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]')))
    email_field.send_keys(mail_address)
    print("Email address inserted")
  except TimeoutException:
    print("email field is not ready")
    pass

@fail_with_error("Cannot click login button")
def google_click_login_button(driver):
  try:
    login_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="identifierNext"]')))
    login_button.click()
    print("Login button clicked")
  except TimeoutException:
    print("login button is not ready")
    pass

@fail_with_error("Cannot set email password")
def google_set_password(driver, password):
  try:
    password_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')))
    password_field.send_keys(password)
    print("Password inserted")
  except TimeoutException:
    print("password field is not ready")
    pass

@fail_with_error("Cannot click next button")
def google_click_next_button(driver):
  try:
    next_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwordNext"]')))
    next_button.click()
    print("Next button clicked")
  except TimeoutException:
    print("next button is not ready")
    pass

def google_is_security_question_required(driver):
  try:
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div')))
    return element.text != "Request lacked state, may have been forged"
  except:
    pass
  return True

@fail_with_error("Cannot select security question as a login method")
def google_select_security_question_as_login_method(driver):
  try:
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[1]')))
    element.click()
    print("Log with security question")
  except TimeoutException:
    print("security question field is not ready")
    pass

@fail_with_error("Cannot set security answer")
def google_set_security_ansver(driver, answer):
  try:
    security_question_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[2]/div/div[1]/div/div[1]/input')))
    security_question_field.send_keys(answer)
    print("Security question answer inserted")
  except TimeoutException:
    print("security question answer field is not ready")
    pass

@fail_with_error("Cannot confirm security answer")
def google_confirm_security_question(driver):
  try:
    security_question_confirm_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button')))
    security_question_confirm_button.click()
    print("Security question confirm button clicked")
  except TimeoutException:
    print("security question confirm button is not ready")
    pass

def googleLogin(mail, driver) :
  print("gmail logging in...")
  driver.get('https://accounts.google.com/signin/oauth/identifier?client_id=717762328687-iludtf96g1hinl76e4lc1b9a82g457nn.apps.googleusercontent.com&scope=profile%20email&redirect_uri=https%3A%2F%2Fstackauth.com%2Fauth%2Foauth2%2Fgoogle&state=%7B%22sid%22%3A1%2C%22st%22%3A%2259%3A3%3ABBC%2C16%3A9b15b0994c6df9fc%2C10%3A1591711286%2C16%3A66b338ce162d6599%2Ca78a0c663f0beb12c0559379b61a9f5d62868c4fbd2f00e46a86ac26796507a1%22%2C%22cdl%22%3Anull%2C%22cid%22%3A%22717762328687-iludtf96g1hinl76e4lc1b9a82g457nn.apps.googleusercontent.com%22%2C%22k%22%3A%22Google%22%2C%22ses%22%3A%22921f8f04441041069683cc2377152422%22%7D&response_type=code&o2v=1&as=NCQvtBXI4prkLLDbn4Re0w&flowName=GeneralOAuthFlow')
  # driver.get('http://mail.google.com/mail?nocheckbrowser')
  # print("mail : ", mail)
  mail_address = mail[1]
  mail_pass = mail[2]
  mail_active = mail[3]
  # mail_address = "mertviy333@gmail.com"
  # mail_pass = "Mertviy23$"
  # time.sleep(3)
  print("opend browser")
  google_set_login(driver, mail_address)
  google_click_login_button(driver)
  google_set_password(driver, mail_pass)
  google_click_next_button(driver)

  if google_is_security_question_required(driver):
    google_select_security_question_as_login_method(driver)
    google_set_security_ansver(driver, mail_active)
    google_confirm_security_question(driver)

  # return # for now      
  # try:
  #   driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[1]/form/div/div/div/div/div/input[1]').send_keys(mail_address)
  #   driver.find_element_by_xpath( '/html/body/div/div[2]/div[2]/div[1]/form/div/div/input' ).click()

  #   time.sleep(3)
  #   driver.find_element_by_id( 'password' ).send_keys(mail_pass)
  #   driver.find_element_by_xpath( '/html/body/div[1]/div[2]/div/div[2]/form/span/div/input[2]' ).click()
  #   time.sleep(3)
  # except:
  #   pass

def gmailSpam(driver) :
  # time.sleep(5)
  driver.get("http://mail.google.com/mail?nocheckbrowser")

  # got it click popup
  try:
    driver.find_element_by_xpath('//*[@id="bubble-434"]/div/div[2]/div[2]').click()
    print("clicked got it in popup")
  except:
    pass
  # Get blocks until a page is loaded, no need 
  #time.sleep(1)
  try :
    driver.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div/div[2]/span/span[2]/div').click()
    time.sleep(1)
    driver.find_element_by_xpath( '/html/body/div[7]/div[3]/div/div[2]/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div/div[3]/div/div[1]/div/div[5]/div/div/div[2]/span/a' ).click()
    time.sleep(3)
    spam = driver.find_element_by_css_selector('table.cf.TB tbody tr.TD td.TC')
    if spam.text == "Hooray, no spam here!" :
      return
  except:
    # driver.quit()
    pass
  
def gmailInbox(driver, proxy) :
  # time.sleep(3)
  # driver.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div/div[1]/div/div/div[2]/span/a').click()
  driver.get("http://mail.google.com/mail?nocheckbrowser")

  # got it click popup
  try:
    driver.find_element_by_xpath('/html/body/div[28]/div[1]/div/div[2]/div[2]').click()
    print("clicked got it in popup")
  except:
    pass

  try:
    inbox_node = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[3]/div/div[2]/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div/div[1]/div/div/div[2]/span/an')))
    inbox_node.click()
    print("Inbox node clicked")
    try:
      trArr = driver.find_elements_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div[8]/div/div[1]/div[3]/div/table/tbody/tr')
    
      for i in trArr :
        email = i.find_element_by_css_selector('td.yX.xY div.yW span.bA4 span').get_attribute('email')
        
        if email.find("mylife.com") >= 0 or email.find('mail.mylife.com') >= 0 or email.find("transaction.mylife.com") >= 0 :
            i.find_element_by_css_selector('td.yX.xY div.yW span.bA4 span').click()
            time.sleep(5)
            i.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div[2]/div/table/tr/td[1]/div[2]/div[2]/div/div[3]/div[3]/div/div/div/div/div[2]/div/div/div/table/tbody/tr/td[2]/div/div/span[1]').click()
            time.sleep(2)
            for ind in Responses :
                i.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div[2]/div/table/tr/td[1]/div[2]/div[2]/div/div[3]/div/div/div/div/div/div[2]/div/div/div/div[4]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div[2]/div[1]/div/table/tbody/tr/td[2]/div[2]/div/div[1]').text += ind[1]
            time.sleep(3)
            driver.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div/table/tr/td[1]/div[2]/div[2]/div/div[3]/div/div/div/div/div/div[2]/div/div/div/div[4]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div[2]/div[1]/div[4]/table/tbody/tr/td[1]/div/div[2]/div[1]').click()
        spam = 0
        for ind in SpamDomains :
            if email.find(ind[1]) > 0:
                spam = 1
                break
        if spam == 1 :
            i.find_element_by_css_selector('td.yX.xY div.yW span.bA4 span').click()
            time.sleep(5)
            driver.find_element_by_xpath('/html/body/div[7]/div[3]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/div').click()
            time.sleep(3)
            driver.find_element_by_xpath('/html/body/div[36]/div[3]/button[1]').click()
        if email.find("mylife.com") >= 0 or email.find('mail.mylife.com') >= 0 or email.find("transaction.mylife.com") >= 0 :
            obj = []
            obj.append(proxy)
            obj.append(email)
            obj.append('messages_opened')
            obj.append('clicked')
            obj.append('')
            obj.append('')
            if spam == 1 :
                obj.append('moved')
                obj.append('marked as spam')
            obj.append(datetime.datetime.now())
            dataSave(driver, obj)
        print(email)      
    except:
      pass
  except TimeoutException:
    print("Inbox Node is not ready")
    pass


def yahooLogin(mail, driver) :
  driver.get("https://login.yahoo.com/config/login")
  mail_address = mail[1]
  mail_pass = mail[2]
  time.sleep(3)
  driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div[2]/form/div[1]/div[3]/input').send_keys(mail_address)
  driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div[2]/form/div[2]/input').submit()
  time.sleep(3)
  try:
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/form/div[2]/input').send_keys(mail_pass)
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/form/div[3]/button').click()
    time.sleep(1)
    driver.get('https://mail.yahoo.com/')
  except:
    pass

def yahooMailSpam(driver) :
  time.sleep(2)
  try:
    driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div[1]/nav/div/div[3]/div[1]/ul/li[7]/div/a/span[1]/span/span/span').click()
    time.sleep(1)
    SpamDomains = [
      ["1", "selflove.com", ""]
    ]
    try :
      liArr = driver.find_elements_by_css_selector('div.p_R.Z_0.iy_h ul.M_0.P_0 li.H_A.hd_n.p_a.L_0.R_0')
      print("Spam liArr : ", liArr)
      for i in liArr :
        try :
          email = i.find_element_by_css_selector('div div.D_F.o_h.ab_C div.D_F.o_h.G_e span')
          email = email.get_attribute('title')
          print(email)
          spam = 0
          for ind in SpamDomains :
              if email.find(ind[1]) > 0:
                  spam = 1
                  break
          if spam == 1 :
              i.find_element_by_css_selector('div div.D_F.o_h.ab_C div.D_F.o_h.G_e span').click()
              time.sleep(2)
              driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[1]/ul/li[4]/div/button/span/span/span').click()
          else :
              print("no spam")
        except :
          continue
    except :
      print("no spam")
      pass
  except:
    pass

def yahooMailInbox(driver, proxy) :
    try:
      driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div[1]/nav/div/div[3]/div[1]/ul/li[1]/div/a/span[1]/span/span/span').click()
    except:
      pass
    time.sleep(2)
    Responses = [
        ['1', 'thanks', ''],
        ['2', 'great', ''],
        ['3', 'call you later', '']
    ]
    try :
        liArr = driver.find_elements_by_css_selector('div.p_R.Z_0.iy_h.iz_A.W_6D6F.H_6D6F.k_w.em_N.c22hqzz_GN ul li')
        print("Inbox liArr : ", liArr)
        for i in liArr :
            try :
                email = i.find_element_by_css_selector('div div.D_F.o_h.ab_C div.D_F.o_h.G_e span')
                email = email.get_attribute('title')
                print("email : ", email)
                
                if email.find("mylife.com") >= 0 or email.find('mail.mylife.com') >= 0 or email.find("transaction.mylife.com") >= 0 :
                    i.find_element_by_css_selector('div div.D_F.o_h.ab_C div.D_F.o_h.G_e span').click()
                    time.sleep(2)
                    driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[1]/ul/li[1]/button/span').text
                    time.sleep(1)
                    for ind in range(len(Responses)) :
                        res_txt = driver.find_element_by_css_selector('div.D_F.ek_BB.em_N div.p_R.cZ1RN91d_GG.k_w.W_6D6F.em_N.D_F div.rte.em_N.ir_0.iy_A.iz_h.N_6Fd5')
                        res_txt.find_element_by_css_selector('div[' + (ind + 1) + ']').text = Responses[ind][1]
                        time.sleep(1)
                    driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[2]/div[2]/ul/li[2]/div/div/div[2]/div[2]/div[1]/button/span').click()
                    time.sleep(2)
                spam = 0
                for ind in SpamDomains :
                    if email.find(ind[1]) > 0:
                        spam = 1
                        break
                if spam == 1 :
                    i.find_element_by_css_selector('div div.D_F.o_h.ab_C div.D_F.o_h.G_e span').click()
                    time.sleep(2)
                    driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]/ul/li[4]/div/button/span/span/span').click()
                if email.find("mylife.com") >= 0 or email.find('mail.mylife.com') >= 0 or email.find("transaction.mylife.com") >= 0 :
                    obj = []
                    obj.append(proxy)
                    obj.append(email)
                    obj.append('messages_opened')
                    obj.append('clicked')
                    obj.append('')
                    obj.append('')
                    if spam == 1 :
                        obj.append('moved')
                        obj.append('marked as spam')
                    obj.append(datetime.datetime.now())
                    dataSave(driver, obj)
            except :
                continue
    except :
        print("empty mail")
        pass

def dataSave(driver, obj) :
    query = "insert into usagelog (id, proxies_id, emailAdresses_id, number_opened, number_clicked, number_retreived_from_spam, number_spam, timestamp)"
    query += " values ('')"
    query += " values ('" + obj[0] + "', "
    query += "'" + obj[1] + "', "
    query += "'" + obj[2] + "', "
    query += "'" + obj[3] + "', "
    query += "'" + obj[4] + "', "
    query += "'" + obj[5] + "', "
    query += "'" + obj[6] + "');"
    DB.execute(query)
    driver.quit()
getEmailAdresses()
getProxies()
getBrowser()
getSpamDomains()
getResponses()

openPage()