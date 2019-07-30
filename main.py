import requests
import pprint
from bs4 import BeautifulSoup as bs
import ast

class Login:
    s = requests.session()
    r = s.get('https://portal.ncu.edu.tw/login')

    NID = s.cookies['NID']
    j_session_id = s.cookies['JSESSIONID']

    username = input('username: ')
    password = input('password: ')
    job_content = input('job_content: ')

    s.post(
        "https://portal.ncu.edu.tw/login/j_spring_security_check",
        headers=dict(Referer="https://cis.ncu.edu.tw/HumanSys/home"),
        data={
            "j_username":username,
            "j_password":password
        }
    )

    res = s.get('https://cis.ncu.edu.tw/HumanSys/student/stdSignIn')
    soup = bs(res.text,'html.parser')
    a_tags = soup.find_all('a')
    for tag in a_tags:
        if tag.text == '新增簽到':
            href = tag['href']

    res = s.get("https://cis.ncu.edu.tw/HumanSys/student/{}&msg=signin_ok".format(href))
    soup = bs(res.text,'html.parser')
    input_tags = soup.find_all('input')
    in_or_out = 'in'
    for tag in input_tags:
        tag_id = tag.get('id')
        if tag_id == 'idNo':
            id_no = tag['value']
        if tag_id == 'ParttimeUsuallyId':
            parttime_id = tag['value']
        if tag_id == 'signout':
            in_or_out = 'out'
        if 'name' in tag.attrs:
            if tag['name'] == '_token':
                token = tag['value']

    #print('idNo: ', no_id)
    #print('partim_id: ', parttime_id)
    #print('_token:',token)

    data = {
        "functionName": "doSign",
        "idNo": id_no,
        "ParttimeUsuallyId": parttime_id,
        "AttendWork": job_content,
        "_token":token
    }

    
    r = s.post(
        "https://cis.ncu.edu.tw/HumanSys/student/stdSignIn_detail",
        headers=dict(Referer="https://cis.ncu.edu.tw/HumanSys/student/{}&msg=signin_ok".format(href)),
        data=data
    )
    soup = bs(
        r.text,
        'html.parser'
    )

    try:
        if ast.literal_eval(soup.prettify())['isOK'] == "Y":
            print('sign {}'.format(in_or_out),' OK')
        else:
            print('Error')
    except:
        print('Error')
    
def main():
    l = Login()

if __name__ == '__main__':
    main()


"""
url = "https://portal.ncu.edu.tw/login;jsessionid={}".format(j_session_id)
r = s.post("https://portal.ncu.edu.tw/login/j_spring_security_check",headers=dict(Referer=url),data={"j_username":username,"j_password":password})
r = s.get("https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=xxxxx")
<input type="hidden" id="ParttimeUsuallyId" name="ParttimeUsuallyId" value="xxxxx">
<input type="hidden" id="idNo" name="idNo" value="xxxxxx">
"""