import os,time
from selenium import  webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import threading
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as Wait
import pandas as pd
import time, os



thread_max_limit = 1 # modify suitable values
csv_path = '../dataset/vrn/fairface-head-pose.csv'
data_save_path = '../dataset/fairface-3d/tmp/image'
if not os.path.isdir(data_save_path):
	os.makedirs(data_save_path, exist_ok=True)
obj_path = 'obj'

# selenium
class WebDriver(object):
    def __init__(self):
        self.driver = None

    def open(self,objName,yaw,pitch):
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-site-isolation-trials")
            self.driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
        self.driver.set_window_size(800, 800)
        self.driver.get('file://{}/index.html?id={}&yaw={}&pitch={}'.format(os.getcwd(),objName,yaw,pitch))

    def screenshot(self,name):
        self.driver.get_screenshot_as_file("{}.png".format(name))
        image = Image.open("{}.png".format(name))
        image = image.crop((20, 20, 400, 400))
        image = image.convert("RGB")
        image.save(os.path.join(data_save_path,"{}.jpg".format(name)))
        os.remove("{}.png".format(name))
    
    def close(self):
        if self.driver is not None:
            self.driver.close()

class MyThread(threading.Thread):
  def __init__(self, name,angle):
    threading.Thread.__init__(self)
    self.name = name
    self.angle=angle
    self.webDrive = WebDriver()
    self.first = True

  def run(self):
    for yaw in [-75,-60,-45,-30,-15,0,15,30,45,60,75]:
        for pitch in [-45,-30,-15,0,15,30,45]:
            if os.path.isfile(os.path.join(data_save_path,"{}_75_45.jpg".format(os.path.splitext(self.name)[0]))):
                continue
            if os.path.isfile(os.path.join(data_save_path,"{}_{}_{}.jpg".format(os.path.splitext(self.name)[0],yaw,pitch))):
                continue
            self.webDrive.open(self.name,yaw + self.angle[0],pitch - self.angle[1])
            if self.first:
                time.sleep(10)
                self.first = False
            else:
                time.sleep(1)
            print("creat {}_{}_{}".format(os.path.splitext(self.name)[0],yaw,pitch))
            self.webDrive.screenshot("{}_{}_{}".format(os.path.splitext(self.name)[0],yaw,pitch))
    self.webDrive.close()

if __name__ == '__main__':
    face = {}
    df = pd.read_csv(csv_path)
    c = 0
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        if abs(row["yaw"]) <= 8 and abs(row["pitch"])<= 8 and abs(row["roll"]) <= 8:
            face["{}.obj".format(c)] = [row["yaw"],row["pitch"],row["roll"]]
        c += 1
    threads = []
    for i in tqdm(os.listdir(obj_path)):
        if i not in face:
            continue
        threads.append(MyThread(i,face[i]))
        threads[len(threads)-1].start()
        if len(threads) >= thread_max_limit:
            for x in range(len(threads)):
                threads[x].join()
            threads = []
    for x in range(len(threads)):
        threads[x].join()
    print('done')