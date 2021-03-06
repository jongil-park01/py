from tkinter import *
import requests, json
import sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import myImageLib
import time


window = Tk() # 윈도우이름=tkinter.Tk()를 이용하여 가장 상위 레벨의 윈도우 창을 생성
window.title("ggoorr crawler gui")
window.geometry("640x480") # 가로 * 세로

topFrame = Frame(window)
topFrame.pack(side = TOP)
 
bottomFrame = Frame(window)
bottomFrame.pack(side=BOTTOM)


titleLabel=Label(topFrame, text="시작 버튼을 클릭하면 크롤링을 시작합니다.")
titleLabel.pack()

logLabel=Label(bottomFrame, width=640, height=33)
logLabel.config(text="로그 한줄 추가요.")
logLabel.config(text="로그 한줄 추가요.")
logLabel.pack()

# txt = Text(bottomFrame, width=640, height=33)
# txt.insert(END, "로그는 여기를 보세요. 1\n")
# time.sleep(1)
# txt.insert(END, "로그는 여기를 보세요. 2\n")
# time.sleep(1)
# txt.pack()


#전역 변수 설정X
GGOORR_MAIN_URL = "https://ggoorr.net"                              #꾸르 메인 주소
GGOORR_DETAIL_URL = 'https://ggoorr.net/index.php?mid=all&page='    #꾸르 상세 주소
headers = {'User-Agent': 'Mozilla/5.0'}                             #봇 방지 웹사이트 회피

# 파일 변수 글로벌로 이동
nowDate = datetime.now()
f = open(nowDate.strftime('%Y-%m-%d') + '.txt', mode='wt', encoding='utf-8') #파일 작성 시간이 길어져서 년월일로 파일명 생성                                                            #함수에서 바로 사용하려고 전역으로 설정

#상세 게시글 HTML 수집 함수X
def getDetail(title, detailUrl):

    # 상세 주소 요청 및 응답 수신
    detailRes = requests.get(detailUrl, headers=headers)

    #HTTP 응답 성공 200
    if detailRes.status_code == 200:
        
        #게시글의 HTML을 받아 BeautifulSoup 로 파싱 저장 
        detailHtml = detailRes.text
        detailSoup = BeautifulSoup(detailHtml, 'html.parser')
        
        #article 태그만 데이터만 사용함
        articleBody = detailSoup.find('article')  #article 태그 찾기 

        #GIF 최적화 문자열이 있는 article은 PASS 2021.01.03 추가
        articleBodyText = str(articleBody)
        articleBodyGIFText = articleBodyText.find("GIF 최적화")
        if articleBodyGIFText >=0:
            logLabel.insert(END, ("articleBodyGIFText >=0 is pass...\n"))
            return

        # articleBody 에서 div 영역을 찾아서, p 로 바꿈...
        xeContentDiv = articleBody.div.div.contents
        xeContentDivStr = str(xeContentDiv)
        xeContentDivStr = xeContentDivStr.replace("<div","<p")
        xeContentDivStr = xeContentDivStr.replace("div>","p>")        
        articleBody = BeautifulSoup(xeContentDivStr, 'html.parser')

        #게시글 머릿말/꼬리말 설정
        articleHeader = '<article><div id="article_1"><div>'
        articleTail = '</div></div></article>'
 
        #01 게시글 앞에 머릿말 추가
        articleString = articleHeader

        #02 article 태그 안에서 <p>태그들을 찾아서 저장함
        for pLine in articleBody.select("p"):

            # 이미지 태그가 있는경우, 이미지의 사이즈를 체크 및 수정
            for img in pLine.select("img"):
                imgSrcText = str(img['src'])
                del img['style']
                # txt.insert(END, (imgSrcText)
                if imgSrcText == "None":
                    pass
                elif ".daumcdn.net" in imgSrcText:
                    img['src'] = imgSrcText.replace("R1024x0", "R800x0")
                else:
                    imgArr = myImageLib.getImageInfo( img['src'] )
                    # txt.insert(END, (str(imgArr))
                    if imgArr != None and len(imgArr) == 3 and int(imgArr[1]) > 800:
                        img['width'] = 800

            
            #유튜브 주소를 찾아서 링크 url 변경 처리, 유튜브 주소 없을경우는 변경없이 저장
            pLineText = str(pLine)
            utubeShrotUrlIndex  = pLineText.find('https://youtu.be/')               #유튜브 짧은 주소 접두어
            utubeUrlIndex       = pLineText.find('https://youtube.com/watch?v=')    #유튜브 긴 주소 접두어
            utubeKey = ""       #유튜브 키값 초기화 2021.01.03 추가
            utubeKeyIndex = 0   #유튜브 키값 초기화 2021.01.03 추가

            #유튜브 주소 길이 판단
            if utubeShrotUrlIndex >= 0:
                utubeKeyIndex = pLineText.find('https://youtu.be/')
                utubeKey = pLineText[utubeKeyIndex+17:utubeKeyIndex+17+11] #파싱 수정 2021.01.03 추가
                #유튜브 키값을 iframe 태그로 변경
                tempStr = '<p><iframe style="width:560; height:315px" src="https://www.youtube.com/embed/' + utubeKey + '?rel=0&vq=hd1080" frameborder="0" allowfullscreen></iframe>'
            elif utubeUrlIndex >= 0:
                utubeKeyIndex = pLineText.find('https://youtube.com/watch?v=')
                utubeKey = pLineText[utubeKeyIndex+28:utubeKeyIndex+28+11] #파싱 수정 2021.01.03 추가
                #유튜브 키값을 iframe 태그로 변경
                tempStr = '<p><iframe style="width:560; height:315px" src="https://www.youtube.com/embed/' + utubeKey + '?rel=0&vq=hd1080" frameborder="0" allowfullscreen></iframe>'
            else:
                #유튜브 주소가 없을 경우 변경 없음
                tempStr = pLineText

            #줄 끝에 줄 바꿈 처리
            articleString += tempStr + "\n"
        # end of [for pLine in articleBody.select("p"):]

        #03 게시글 끝에 꼬릿말 추가
        articleString += articleTail   
        
        #04 3가지 변경 작업
        #04-01 cdn.ggoorr.net은 프록시 서버 경유
        articleString = articleString.replace("https://cdn.ggoorr.net", "https://t1.daumcdn.net/thumb/R0x0/?fname=https://cdn.ggoorr.net")
        #04-02 img 태그 앞에 줄 바꿈
        articleString = articleString.replace("<img", "<p><img")
        #04-03 img 폭을 800 2020.12.29 추가
        #articleString = articleString.replace("<img", "<img width=800")
        
        #파일에 저장
        fileContent = "<p>" + title + "</p>" #게시글 제목 앞에 <p> 추가, 제목 뒤에 </p> 추가. 2021.01.03 추가
        fileContent += "\n"
        fileContent += articleString
        fileContent += "\n"
        if (f is not None) and f.write(fileContent):
            logLabel.config(text="fileContent write OK \n")
    else :
        logLabel.config(text=" >>>> GET ERROR..... \n")
    
    #logLabel.config(text="------------------------------------ end of getDetail -----------------------------------")

# 게시판 목록 처리 함수 : 게시글 목록에서 해당 게시물이 작성 대상인 경우 게시글 상세 처리(getDetail)를 호출
# 게시글 처리 대상 - 전일 오전 7시 ~ 당일 오전 6시 59분 59초
def searchList(page):

    logLabel.config(text="=========================================== " + str(page) + " page start ===================================== \n")
    res = requests.get(GGOORR_DETAIL_URL + str(page), headers=headers)

    if res.status_code == 200:
        #응답 html코드를 text로 변환
        html = res.text

        #응답받은 html코드를 BeautifulSoup에 사용하기 위하여 인스턴스 지정
        soup = BeautifulSoup(html, 'html.parser')

        #tbody 에 필요한 게시글 목록이 있어 해당 영역 가져오기 처리
        tbody = soup.select('.bd_tb_lst tbody')
        contentsBody = tbody[0]

        nCnt = 0 # 게시글 처리 순서 저장
        #tr - 개별 게시글 확인
        for trOne in contentsBody.select('tr'):
            logLabel.config(text="--------------------------------------- [ " + str(page) + " page / " + str(nCnt) + " line ] --------------------------------------- \n")

            #공지글은 생략
            if None != trOne.get('class'):
                if ("notice" == trOne['class'][0]):
                    logLabel.config(text="공지는 PASS!! \n")
                    nCnt+=1
                    continue
            else:
                cate = ""
                title = ""
                author = ""
                time1 = ""
                time2 = ""
                detailUrl = ""
                timenumber = ""
                writetime = ""

                #td 확인
                for tdTag in trOne.select('td'):
                    classNm = tdTag["class"][0]
                    if classNm == "cate":
                        #카테고리
                        cate = tdTag.get_text()
                    elif classNm == "title":
                        #제목 및 URL
                        alist = tdTag.find_all('a', class_="hx")
                        title = alist[0].get_text().strip().replace("\n", "")
                        detailUrl = GGOORR_MAIN_URL + alist[0]['data-viewer']
                    elif classNm == "author":
                        #작성자
                        author = tdTag.get_text()
                    elif classNm == "time":
                        time1 = tdTag.get_text()        #1일 이내는 N분 전/N시간 전, 1일 이후는 날짜
                        time2 = tdTag.attrs['title']    #1일 이내는 N분 전/N시간 전, 1일 이후는 시간

                        if '분' in time1:
                            #분일 경우 작성 시간 확인
                            timenumber = time1[0:time1.find('분')]
                            writetime = datetime.today() - timedelta(minutes=int(timenumber))
                        elif '시간' in time1:
                            #시간일 경우 작성 시간 확인
                            timenumber = time1[0:time1.find('시간')]
                            writetime = datetime.today() - timedelta(hours=int(timenumber))
                        else:
                            #분과 시간이 아니면 날짜와 시간을 조합
                            writetime = datetime.strptime((time1 + " " + time2), '%Y.%m.%d %H:%M')
                    else:
                        pass
                # end of [for tdTag in trOne.select('td'):]

                # 게시물 1개에 대한 처리여부 확인 로직 시작......
                logLabel.config(text="category : " + cate + "\n")
                logLabel.config(text="title : " + title + "\n")
                logLabel.config(text="author : " + author + "\n")
                logLabel.config(text="writetime : " + writetime.strftime('%Y-%m-%d %H:%M:%S') + "\n")
                logLabel.config(text="detailUrl : " + detailUrl + "\n")

                #전일 오전 7시
                yesterday = datetime.today() - timedelta(days=1)
                fromdate = datetime(yesterday.year, yesterday.month, yesterday.day, 7, 0, 0)

                #당일 오전 6시 59분 59초
                todate = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 6, 59, 59)

                if(writetime > todate):
                    logLabel.config(text="작성은 안하지만, 다음 게시물 조회" + "\n")
                    pass
                elif writetime <= fromdate:
                    logLabel.config(text="작성 대상 아님 - 더이상 게시물 조회하지 않음" + "\n")
                    return False
                else :
                    logLabel.config(text="작성 대상 맞음" + "\n")
                    getDetail(title, detailUrl)

            nCnt+=1
            # end of [for trOne in contentsBody.select('tr'):]
        
        return True
        logLabel.config(text="=========================================== end of List =====================================" + "\n")
    else :
        logLabel.config(text="GGOORR_DETAIL_URL + str(page) + " + ">>>> GET ERROR....." + "\n")

# youtube test
# getDetail("title", "https://ggoorr.net/enter/10765153")
# sys.exit()

# gif test
#getDetail("title", "https://ggoorr.net/thisthat/10768975")
#sys.exit()

# 문제의 <p>태그없이 이미지만 있는 게시물 > 해결 안됨 > 처리 룰 필요..!!
#getDetail("title", "https://ggoorr.net/enter/10770855")
#sys.exit()

# 문제의 <p>태그없이 href 만 있는 게시물 > 해결 안됨 > 처리 룰 필요..!!
# getDetail("title", "https://ggoorr.net/all/10815964")
# sys.exit()

# 이미지 가로 사이즈 800 이상
#getDetail("title", "https://ggoorr.net/all/10857189")
#sys.exit()

# 이미지를 daum cdn 을 통해 서비스 하는 경우 - img1.daumcdn.net
# getDetail("title", "https://ggoorr.net/all/10898864")
# sys.exit()

# 이미지를 daum cdn 을 통해 서비스 하는 경우  - t1.daumcdn.net
# getDetail("title", "https://ggoorr.net/all/10894836")
# sys.exit()

#이미지를 daum cdn 을 통해 서비스 하는 경우  - t1.daumcdn.net
# getDetail("title", "https://ggoorr.net/all/10893852")
# sys.exit()


# 메인 시작 : 1-20 페이지까지 for loop
def startCrawlering():
    for page in range(1, 20):
        if False == searchList(page):
            break

    if f is not None:
        f.close  


startBtn = Button(topFrame, text="버튼1", padx=5, pady=10,  command=startCrawlering, repeatdelay=1000)
startBtn.pack()
# startBtn.place(x= 100, y= 100)

window.mainloop()    # 윈도우 창을 윈도우가 종료될 때 까지 실행