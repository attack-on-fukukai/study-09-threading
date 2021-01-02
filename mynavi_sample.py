import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import math
import threading
from multiprocessing import Pool


# 出力先のCSVファイル名
csvFileName = '希望の仕事.csv'


### Chromeを起動する関数
def set_driver(driver_path,headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg==True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    #options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + '\\' + driver_path,options=options)   


### ファイルを削除する
def deleteFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)


### 検索ヒット件数からページ数を求める
def getAllPageCount(resultNum):
    allPageCount = math.ceil(resultNum / 50)
    return allPageCount


### 1ページ分読み込む
def readPage(keyWord,pageNo):
    # driverを起動
    driver=set_driver('chromedriver.exe',False)
    # Webサイトを開く
    driver.get(f'https://tenshoku.mynavi.jp/list/kw{keyWord}/pg{pageNo}/')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(\'.karte-close\').click()')
    
    names = []
    copys = []
    statuss = []
    body0s = []
    body1s = []
    body2s = []
    body3s = []
    body4s = []

    elem_cassetteRecruit__contents = driver.find_elements_by_class_name('cassetteRecruit__content')
    for elem_cassetteRecruit__content in elem_cassetteRecruit__contents:

        # 会社名を取得する
        name = elem_cassetteRecruit__content.find_element_by_class_name('cassetteRecruit__name').text

        # コピーを取得する
        copy = elem_cassetteRecruit__content.find_element_by_class_name('cassetteRecruit__copy').text

        # 雇用形態を取得する
        status = elem_cassetteRecruit__content.find_element_by_class_name('labelEmploymentStatus').text

        # 仕事内容 ～ 初年度年収を取得する
        elem_tableCondition__bodys = elem_cassetteRecruit__content.find_element_by_class_name('tableCondition').find_elements_by_class_name('tableCondition__body')

        body0 = elem_tableCondition__bodys[0].text
        body1 = elem_tableCondition__bodys[1].text
        body2 = elem_tableCondition__bodys[2].text
        body3 = elem_tableCondition__bodys[3].text
        if int(len(elem_tableCondition__bodys)) == 5:
        # 初年度年収が載っている案件
            body4 = elem_tableCondition__bodys[4].text
        else:
        # 初年度年収が載っていない案件
            body4 = ''

        names.append(name)
        copys.append(copy)
        statuss.append(status)
        body0s.append(body0)
        body1s.append(body1)
        body2s.append(body2)
        body3s.append(body3)
        body4s.append(body4)
    
    df = pd.DataFrame()
    df['会社名'] = names
    df['コピー'] = copys
    df['雇用形態'] = statuss
    df['仕事内容'] = body0s
    df['対象となる方'] = body1s
    df['勤務地'] = body2s
    df['給与'] = body3s
    df['初年度年収'] = body4s

    # 検索結果をcsvファイルに書き込む
    df.to_csv(csvFileName,index=False,header=None,mode='a')


### main処理
def main(search_keyword):

    # 前に出力したcsvファイルを削除する
    deleteFile(csvFileName)

    # driverを起動
    driver=set_driver('chromedriver.exe',False)
    # Webサイトを開く
    driver.get('https://tenshoku.mynavi.jp/')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(\'.karte-close\').click()')
    # ポップアップを閉じる
    #driver.execute_script('document.querySelector('.karte-close').click()')
    # 検索窓に入力
    driver.find_element_by_class_name('topSearch__text').send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name('topSearch__button').click()
        
    #検索結果の件数を取得する
    time.sleep(20)
    _resultNum = driver.find_element_by_class_name('result__num').text    
    _resultNum = _resultNum.replace('件','')
    resultNum = int(_resultNum)

    if resultNum > 0:
    # 入力したキーワードで検索がヒットした場合
        # ヒット件数から総ページ数を求める
        allPageCount = getAllPageCount(resultNum)

        ts = []
        for i in range(allPageCount):
            pageNo = i + 1
             # 1ページ分読み込む
            ts.append(threading.Thread(target=readPage,args=(search_keyword,pageNo)))

        # 処理速度の計測開始
        startTime = time.perf_counter()

        for t in ts:
            t.setDaemon(True)
            t.start()
            t.join()

        # 処理速度の計測終了
        totalTime = math.floor(time.perf_counter() - startTime)
        print(f'処理速度：{totalTime}秒')
    else:
    #入力したキーワードで検索がヒットしなかった場合
        print('希望の仕事は見つかりませんでした')


### 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == '__main__':

    search_keyword =input('希望するキーワードを入力してください >>> ')
    main(search_keyword)
