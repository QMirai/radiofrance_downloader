from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
import time
import requests
import re
import os
import subprocess
import threading


folder_path = None
buttons_num = 0
filename_src = []


def __clean_name(filename: str):
    filename = re.sub(r'/', '-', filename)
    invalid_chars = r'[\:*?<>|":]'
    replace_char = ' '
    return re.sub(invalid_chars, replace_char, filename)


class RadioFrance:
    def __init__(self, link, output_path, test):
        self.link = link
        self.output_path = output_path
        self.test = test
        self.filename_src = []
        self.folder_path = None
        self.buttons_num = 0


# TODO: 整理下面的fonction，争取功能分开，工具归类为工具，运行为运行


def close_banner(driver):
    try:
        driver.find_element(By.ID, 'didomi-notice-agree-button').click()
    except Exception as ex:
        print(ex)
    time.sleep(2)


def is_podcast(link):
    pod = re.search(r'podcasts/(.+)', link).group(1)
    if r'/' in pod:
        return False
    else:
        return 'podcasts'


def find_pod_title(driver, pod: bool, output_path):
    if pod:
        # 提取播客标题，以此作为文件夹名
        folder_name = driver.find_element(By.CLASS_NAME, "CoverPodcast-title").text
    else:
        parent = driver.find_element(By.CLASS_NAME, "ParentShowCard-data")
        folder_name = parent.find_element(By.TAG_NAME, 'a').text
    global folder_path
    folder_path = os.path.join(output_path, __clean_name(folder_name))
    os.makedirs(folder_path, exist_ok=True)


def get_audio_radiofrance(link, output_path, test) -> None:
    # 使用WebDriverManager来获取Chrome WebDriver
    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--mute-audio")

    # 创建一个 Chrome WebDriver 实例
    driver = webdriver.Chrome(options=chrome_options)  # executable_path="./chromedriver.exe",

    # 打开网页
    driver.get(link)

    # 关闭 Cookies banner
    close_banner(driver)

    # pod or ep: True / False
    pod = is_podcast(link)

    # 获取Podcast标题，并建立文件夹
    find_pod_title(driver, pod, output_path)

    # loading and downloading
    if pod:
        download_pods(driver, test)
    else:
        download_ep(driver)

    # 关闭浏览器窗口
    driver.quit()


def download_pods(driver, test):
    buttons = driver.find_elements(By.CSS_SELECTOR,
                                   "button.Button.light.primary.small.circular.svelte-3444nd.circular")
    global buttons_num
    buttons_num = len(buttons)
    for button in buttons:

        title = str(button.get_attribute('aria-label'))

        if "Ep " in title:
            episode = re.search(r"Ep\s?\d", title).group()
            content = re.search(r'\s(.*) \|', title).group(1)
            title = episode + " " + content
        else:
            title = __clean_name(title[8:])

        # js 点击
        driver.execute_script("arguments[0].click();", button)

        # 等待媒体文件加载
        time.sleep(5)

        # # 找到包含音频元素的<div>元素
        # div_element = driver.find_element(By.ID, 'player-wrapper')

        # 在<div>元素的范围内查找音频元素
        audio = driver.find_element(By.TAG_NAME, 'audio')

        # 提取音频的src属性
        src = audio.get_attribute('src')
        print(title, src)
        # print(title)
        filename = title + re.search(r"\.\w{3}$", src).group()
        filename_src.append((filename, src))
        e.set()

        if test:
            break


def download_ep(driver):
    button = driver.find_element(By.CSS_SELECTOR,
                                   "button.Button.light.primary.large.svelte-3444nd")
    title = driver.find_element(By.CLASS_NAME, "CoverEpisode-title").text
    title = __clean_name(title)

    # js 点击
    # driver.execute_script("arguments[0].click();", button)
    button.click()

    # 等待媒体文件加载
    time.sleep(5)

    # 在<div>元素的范围内查找音频元素
    audio = driver.find_element(By.TAG_NAME, 'audio')

    # 提取音频的src属性
    src = audio.get_attribute('src')
    print(title, src)
    filename = title + re.search(r"\.\w{3}$", src).group()
    filename_src.append((filename, src))
    e.set()


def get_audio_listennote(link, output_path) -> None:
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--mute-audio")

    # 创建一个 Chrome WebDriver 实例
    driver = webdriver.Chrome(options=chrome_options)

    # 打开网页
    driver.get(link)

    # driver.find_element(By.ID, 'didomi-notice-agree-button').click()

    time.sleep(2)

    # 提取播客标题，以此作为文件名
    title = __clean_name(driver.find_element(By.CSS_SELECTOR, 'a.font-bold.ln-l1-text.inline').text)

    # 点击 MORE 按钮，以便出现下载选项
    button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="MORE"]')
    button.click()

    # 找到包含链接的 <a> 元素
    link_element = driver.find_element(By.CSS_SELECTOR, 'a[title="Download audio file"]')

    # 获取链接的 href 属性值
    link = link_element.get_attribute('href')
    driver.get(link)
    newlink = driver.current_url
    filename = title + re.search(r"\.\w{3}$", newlink).group()
    print(filename, newlink)

    # 关闭浏览器窗口
    driver.quit()

    download(link, filename, output_path)

    # response = requests.get(link)
    # if response.status_code == 200:
    #     # 保存音频文件
    #     with open(os.path.join(output_path, filename), "wb") as file:
    #         file.write(response.content)
    #         print(filename, "download successful")
    # else:
    #     print(filename, "download failed")


def download(url, filename, output_path):

    response = requests.get(url)
    if response.status_code == 200:
        # 保存音频文件
        with open(os.path.join(output_path, filename), "wb") as file:
            file.write(response.content)
            print(filename, "download successful")
    else:
        print(filename, "download failed")


def radiofrance_downloader(parallel):
    global filename_src, folder_path

    def aria2c_downloader():
        with lock:
            filename, src = filename_src.pop()
        print('Downloading {}'.format(filename))
        time.sleep(8)
        cmd = f'aria2c -o "{filename}" -d "{folder_path}" "{src}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print('Download completed {}.'.format(filename))
        print(result.stderr)

    with ThreadPoolExecutor(parallel) as executor:
        downloading_file = 0
        while e.wait(timeout=20):                # wait until event.set(), which means that filename_src list receives
            e.clear()                            # a tuple (filename, src), then clear that event for waiting the next.
            executor.submit(aria2c_downloader)   # use threads in the pool to download files.
            downloading_file += 1
            if downloading_file == buttons_num:  # if downloading files number == found files number, it means that all
                break                            # all files are being downloading or downloaded, no need to wait 20s.


def main(link, output_path, parallel, test):
    if "radiofrance" in link:
        finder = threading.Thread(target=radiofrance_downloader, args=(parallel,))
        downloader = threading.Thread(target=get_audio_radiofrance, args=(link, output_path, test))
        finder.start()
        downloader.start()
        finder.join()
        downloader.join()
    elif "listennote" in link:
        get_audio_listennote(link, output_path)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="download audio"
    )

    parser.add_argument('link', type=str,
                        help="link of the web with podcasts")
    parser.add_argument('-p', '--output_path', type=str,
                        default="D:/podcasts",
                        help="output path, default path is D:/podcasts")
    parser.add_argument('-l', "--parallel", default=4,
                        help="parallel download number")
    parser.add_argument('-t', "--test", action="store_true",
                        help="for test")

    args = parser.parse_args()
    e = threading.Event()
    lock = threading.Lock()
    main(args.link, args.output_path, args.parallel, args.test)
