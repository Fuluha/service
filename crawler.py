#　ライブラリの中のクラスをインポート
from logging import basicConfig, getLogger, DEBUG
from scraper import Scraper
import gspread
# JASONの読み書き
import json
# 正規表現
import re
# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials 

# アクセスキーの読み込み
import configparser
# configファイルの読み込み
config = configparser.ConfigParser()
config.read('./config.ini')
# 値を文字列で取得する
# config['json_file']['spreadsheet_key']

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(config['ACCESS_KEY']['json_file'], scope)
#OAuth2の資格情報を使用してGoogle APIにログインする
gc = gspread.authorize(credentials)
#共有設定したスプレッドシートの操作する記述を書く(シート1を開く)
workbook = gc.open_by_key(config['ACCESS_KEY']['spreadsheet_key']).sheet1

################################################################
# ログフォーマットを定義
formatter = "[%(asctime)s][%(name)s][%(levelname)s]%(message)s"
# ログレベル コンソールでのログを非表示にするにはここを読み込ませない
# basicConfig(level=DEBUG, format=formatter)
################################################################

class Crawler:
    """ Crawler
    self.user_agent : ユーザーエージェントの情報を設定
    self.engine : 検索サイトを設定

    get_search_url(word, engine="google") : 検索サイトで検索結果の一覧を取得
        word: 検索するワード
        [engine]: 使用する検索サイト（デフォルトは google）
    """
    def __init__(self, engine="google"):
        # User-Agent
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/69.0.3497.100"
        # engine
        self.engine = engine
    
    # B1セルの値を検索クエリとして受け取り、wordに代入
    word = workbook.acell('B1').value
    def get_search_url(self, word):
    # def get_search_url(self, workbook.acell('B1').value):
        """ get_search_url
        word: 検索するワード
        [engine]: 使用する検索サイト（デフォルトは google）
        """
        logger = getLogger("get_search_url()")
        try:
            if self.engine == "google":
                # google 検索
                search_url = "https://www.google.co.jp/search"
                search_params = {"q": word}
                search_headers = {"User-Agent": self.user_agent}
                # データ取得
                soup = Scraper.get_html(search_url, search_params, search_headers)
                if soup != None:
                    tags = soup.select(".r > a")
                    urls = [tag.get("href") for tag in tags]
                    subheading = [soup.find_all(re.compile("[hH][1-5].*?"))]
                    return urls
                else:
                    raise Exception("No Data")
            else:
                raise Exception("No Engine")
        except Exception as e:
            logger.warning(e)
            return None

if __name__ == '__main__':
    try:
        # インスタンス化
        crawler = Crawler()
        urls = crawler.get_search_url("https://yugioh-sinaprice.com/entry/2020/05/20/120707")
        if urls != None:
            for i,url in enumerate(urls, start=1):
                if Scraper.get_robots_txt(url):
                    soup = Scraper.get_html(url)
                    print(soup.title.get_text())
                    print(url)
                    # workbook.update('B'+str(i+2), url)
                    # workbook.update('C'+str(i+2), soup.title.get_text())
                    for subheading in soup.find_all(re.compile("[hH][1-5].*?")):
                        print(subheading.get_text())
                        workbook.update('D'+str(i+2), subheading.get_text())
                        # headline = soup.find_all(re.compile("^h"))
                        # headline = soup.find_all(h2)
                        # print(soup.h2.get_text())
                        # print("BREAK")
                        # break
                else:
                    print("クロールが拒否されました [{}]".format(url))
        else:
            print("取得できませんでした")
    except Exception as e:
        print("エラーになりました")


# #テスト用のリスト100個値が入ってるものとする
# test_list = ['1','2','3','4'・・・中略,'100']
# #編集する範囲を指定、A1セルから、リストの要素数をカウントしたものを指定する
# cell_list = workbook.range('B3:B'+str(len(soup.title.get_text()_list)))
# #cell_listにtest_listの値を流し込む
# for i,cell in enumerate(cell_list):
#     cell.value = test_list[i]
# #最後にupdate_cellsで流し込む
# workbook.update_cells(cell_list)
