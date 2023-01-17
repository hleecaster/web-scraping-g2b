from email.message import EmailMessage
from smtplib import SMTP_SSL

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

import schedule
import time


SMTP_USER = ""
SMTP_PASSWORD = ""

받는사람 = ""
메일제목 = ""

검색어리스트 = ["", "", ""]


"""메일 발송"""
def send_mail(받는사람, 메일제목, 메일본문):

    # 템플릿 생성
    msg = EmailMessage()

    # 보내는 사람 / 받는 사람 / 제목 / 본문 구성
    msg["To"] = 받는사람.split(",")
    msg["Subject"] = 메일제목
    msg.set_content(메일본문)

    # 메일 발송
    with SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)


"""크롤링"""
def crawl():

    try:
        # 크롬드라이버 https://chromedriver.chromium.org/downloads
        driver = webdriver.Chrome("chromedriver.exe")

        메일본문 = ""

        for query in 검색어리스트:

            # 입찰정보 검색 페이지로 이동
            driver.get('https://www.g2b.go.kr:8101/ep/tbid/tbidFwd.do')
            
            # 업무 종류 체크
            task_dict = {'용역': 'taskClCds5', '민간': 'taskClCds20', '기타': 'taskClCds4'}
            for task in task_dict.values():
                checkbox = driver.find_element(By.ID, task)
                checkbox.click()
            
            # ID값이 bidNm인 태그 가져오기
            bidNm = driver.find_element(By.ID, 'bidNm')
            # 내용을 삭제
            bidNm.clear()
            # 검색어에 문자열 전달
            bidNm.send_keys(query)
            bidNm.send_keys(Keys.RETURN)

            option_dict = {'검색기간 1달': 'setMonth1_1', '입찰마감건 제외': 'exceptEnd', '검색건수 표시': 'useTotalCount'}
            for option in option_dict.values():
                checkbox = driver.find_element(By.ID, option)
                checkbox.click()

            # 목록수 100건 선택 (드롭다운)
            recordcountperpage = driver.find_element(By.NAME,'recordCountPerPage')
            selector = Select(recordcountperpage)
            selector.select_by_value('100')

            # 검색 버튼 클릭
            search_button = driver.find_element(By.CLASS_NAME, 'btn_mdl')
            search_button.click()

            # 검색 결과 확인
            elem = driver.find_element(By.CLASS_NAME,'results')
            div_list = elem.find_elements(By.TAG_NAME, 'div')

            # 리스트 형태로 검색결과 저장
            results = []
            for div in div_list:
                results.append(div.text)
                a_tags = div.find_elements(By.TAG_NAME,'a')
                if a_tags:
                    for a_tag in a_tags:
                        link = a_tag.get_attribute('href')
                        results.append(link)

            # results 리스트에서 12개 단위로 리스트 분할하여 새로운 리스트로 저장 
            result = [results[i * 12:(i + 1) * 12] for i in range((len(results) + 12 - 1) // 12 )]

            # 이메일 본문 구성
            메일본문 += "▶ 키워드: " + query + "\n\n"
            for row in result:
                메일본문 += row[4] + "\n"
                메일본문 += row[6] + "\n"
                메일본문 += row[9] + "\n"
                메일본문 += row[5] + "\n"
                메일본문 += "\n"
            메일본문 += "\n\n"

        return 메일본문

    except Exception as e:
        print(e)

    finally:
        driver.quit()


"""실행"""
def job():
    메일본문 = crawl()
    send_mail(메일제목, 메일본문)


"""실행 스케줄링"""
schedule.every().friday.at("08:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)