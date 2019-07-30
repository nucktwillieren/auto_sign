import requests
import pprint
from bs4 import BeautifulSoup as bs
import ast
import json
import random
import schedule
import time
import threading

def timer():
    while 1:
        try:
            print(time.strftime("%c"))
            time.sleep(3600)
        except:
            break

class NcuWeb:
    def __init__(self,username,password):
        self._username = username
        self._password = password
        self.sign_href = ''
        with open('job_content.json') as f:
            self._job_content_json = json.load(f)
        
    def _restart_ncu_session(self):
        self.s = requests.session()
        self.r = self.s.get('https://portal.ncu.edu.tw/login')
        self.NID = self.s.cookies['NID']
        self.j_session_id = self.s.cookies['JSESSIONID']
    
    def login(self):
        self._restart_ncu_session()
        self.s.post(
            "https://portal.ncu.edu.tw/login/j_spring_security_check",
            headers=dict(Referer="https://cis.ncu.edu.tw/HumanSys/home"),
            data={
                "j_username":self._username,
                "j_password":self._password
            }
        )
    
    def _get_sign_href(self):
        res = self.s.get('https://cis.ncu.edu.tw/HumanSys/student/stdSignIn')
        soup = bs(res.text,'html.parser')
        a_tags = soup.find_all('a')
        for tag in a_tags:
            if tag.text == '新增簽到':
                self.sign_href = tag['href']

    def _get_sign_object(self):
        self._get_sign_href()
        res = self.s.get("https://cis.ncu.edu.tw/HumanSys/student/{}&msg=signin_ok".format(self.sign_href))
        soup = bs(res.text,'html.parser')
        input_tags = soup.find_all('input')

        self.in_or_out = 'in'
        for tag in input_tags:
            tag_id = tag.get('id')
            if tag_id == 'idNo':
                self.id_no = tag['value']
            if tag_id == 'ParttimeUsuallyId':
                self.parttime_id = tag['value']
            if tag_id == 'signout':
                self.in_or_out = 'out'
            if 'name' in tag.attrs:
                if tag['name'] == '_token':
                    self.sign_token = tag['value']

        #print('idNo: ', self.id_no)
        #print('partim_id: ', self.parttime_id)
        #print('_token:',self.sign_token)

    def _get_job_content(self):
        self.job_content = self._job_content_json[random.randint(0,len(self._job_content_json)-1)]                        

    def sign(self,in_or_out):
        if in_or_out == 'reset':
            self.login()
            
        self._get_sign_object()
        self._get_job_content()          

        data = {
            "functionName": "doSign",
            "idNo": self.id_no,
            "ParttimeUsuallyId": self.parttime_id,
            "AttendWork": self.job_content,
            "_token":self.sign_token
        }

        
        res = self.s.post(
            "https://cis.ncu.edu.tw/HumanSys/student/stdSignIn_detail",
            headers=dict(Referer="https://cis.ncu.edu.tw/HumanSys/student/{}&msg=signin_ok".format(self.sign_href)),
            data=data
        )
        soup = bs(
            res.text,
            'html.parser'
        )

        try:
            if ast.literal_eval(soup.prettify())['isOK'] == "Y":
                print(time.strftime("%c"), ' sign {}'.format(self.in_or_out),' OK')
            else:
                print(time.strftime("%c"), ' Error')
        except:
            print(time.strftime("%c"), ',Error')
        
        if in_or_out != 'reset':
            if self.in_or_out.upper() != in_or_out.upper():
                self.sign('reset')
                time.sleep(2)  

def job(username,password,in_or_out):
    n = NcuWeb(username,password)
    n.login()
    n.sign(in_or_out)
    
def main():
    username = input('username: ')
    password = input('password: ')
    threading.Thread(target=timer).start()
    #job(username,password,'out')
    #time.sleep(3)
    #job(username,password,'out')
    
    schedule.every().day.at("08:30").do(job,username=username,password=password,in_or_out='in')
    schedule.every().day.at("20:00").do(job,username=username,password=password,in_or_out='out')

    while 1:
        schedule.run_pending()
        time.sleep(300)

if __name__ == '__main__':
    main()


"""
url = "https://portal.ncu.edu.tw/login;jsessionid={}".format(j_session_id)
r = s.post("https://portal.ncu.edu.tw/login/j_spring_security_check",headers=dict(Referer=url),data={"j_username":username,"j_password":password})
r = s.get("https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=xxxxx")
<input type="hidden" id="ParttimeUsuallyId" name="ParttimeUsuallyId" value="xxxxx">
<input type="hidden" id="idNo" name="idNo" value="xxxxxx">
"""