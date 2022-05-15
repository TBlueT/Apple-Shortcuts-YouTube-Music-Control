from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import ctypes, os, datetime, json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class YouMusic:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.chrome_driver = "chromedriver.exe"
        self.driver = webdriver.Chrome(self.chrome_driver, options=self.chrome_options)

    def Search(self, value):
        http_address = "https://music.youtube.com/search?q=" + value
        self.driver.get(http_address)
        time.sleep(0.5)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
        time.sleep(1)
        rslt = self.driver.find_element_by_xpath("//*[@id='play-button']")
        rslt.click()
        time.sleep(1)
        rslt = self.driver.find_element_by_xpath("//*[@id='right-controls']/tp-yt-paper-icon-button[1]")
        rslt.click()

    def Button(self, value):
        rslt = self.driver.find_element_by_xpath(value)
        rslt.click()
        musicbyline = self.driver.find_elements_by_css_selector(".subtitle")
        titleStr = [[""] for _ in range(len(musicbyline))]
        count = 0
        for i in musicbyline:
            titleStr[count] = i.text
            count += 1
        return titleStr[len(musicbyline)-1]

class json_process:
    def __init__(self):
        self.read_file()
        self.StartTime = datetime.datetime.now().isoformat()
        self.connection_record_data[self.StartTime] = {}
        self.connect_count = 0

    def read_file(self):
        with open("connection record.json", "r") as json_file:
            self.connection_record_data = json.load(json_file)
            json_file.close()
    def write_file(self):
        with open("connection record.json", "w") as json_file:
            json.dump(self.connection_record_data, json_file, indent=4)
            json_file.close()

    def write_json(self, data):
        self.connection_record_data[self.StartTime][F'{self.connect_count}'] = data
        self.connect_count += 1
        self.write_file()

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):

    jp = json_process()
    YM = YouMusic()
    user = ctypes.windll.user32
    UP_Volume = 0xAF
    Down_Volume = 0xAE
    Next_Track = 0xB0
    Prev_Track = 0xB1
    Media_Play_Pause = 0xB3
    play_pause = []
    play_pause = {"but": 0}
    play_pause["Music"] = {"title": 0, "artist": 0}

    def do_GET(self):
        print('get 요청')
        parts = urlparse(self.path)
        connect_time = F"{self.client_address}: {datetime.datetime.now()},'{self.command}, {parts.path}'"
        if os.access('.' + os.sep + parts.path, os.R_OK):
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            keyword, value = parts.query.split('=', 1)
            print(parts.path, keyword, value)
            connect_time += F", {parts.query}"
            if parts.path[1:] == 'Sound':
                if keyword == "volume":
                    if value == "up":
                        self.user.keybd_event(self.UP_Volume, 0, 1, 0)
                        self.response_Ok()
                    elif value == "down":
                        self.user.keybd_event(self.Down_Volume, 0, 1, 0)
                        self.response_Ok()
                elif keyword == "state":
                    if value == "NextTrack":
                        titleName = self.YM.Button('//*[@id="left-controls"]/div/tp-yt-paper-icon-button[5]')
                        self.response_Ok(titleName)
                    elif value == "PrevTrack":
                        titleName = self.YM.Button("//*[@id='left-controls']/div/tp-yt-paper-icon-button[1]")
                        titleName = self.YM.Button("//*[@id='left-controls']/div/tp-yt-paper-icon-button[1]")
                        self.response_Ok(titleName)
                    elif value == "MediaPlayPause":
                        self.YM.Button("//*[@id='play-pause-button']")
                        self.response_Ok()

            elif parts.path[1:] == "name":
                self.YM.Search(value)
                self.response_Ok()

        self.jp.write_json(connect_time)
        print(connect_time)

    def do_POST(self):
        print('post 요청')
        parts = urlparse(self.path)
        connect_time = F"{self.client_address}: {datetime.datetime.now()},'{self.command}, {parts.path}'"
        self.jp.write_json(connect_time)

    def response_Ok(self, value = None):
        self.send_response(200)
        self.send_header('Content-type', 'text')
        self.end_headers()
        if value:
            self.wfile.write(value.encode('utf-8'))

# 자바에서 public static void main() 메소드와 같다.
if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 8080), MyHTTPRequestHandler)
    print('Server Start')
    httpd.serve_forever()
    print('Server End')
    os.close()
