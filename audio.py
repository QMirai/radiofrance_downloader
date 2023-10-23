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

filename_src = []
folder_path = None


def clean_name(filename: str):
    invalid_chars = r"[\\\/\:*?<>|]"
    replace_char = '-'
    return re.sub(invalid_chars, replace_char, filename)


def get_audio_radiofrance(link, output_path, test) -> None:
    # 使用WebDriverManager来获取Chrome WebDriver
    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--mute-audio")

    # 创建一个 Chrome WebDriver 实例
    driver = webdriver.Chrome(options=chrome_options)  # executable_path="./chromedriver.exe",

    # 打开网页
    driver.get(link)

    try:
        driver.find_element(By.ID, 'didomi-notice-agree-button').click()
    except Exception as ex:
        print(ex)

    time.sleep(2)

    # 提取播客标题，以此作为文件夹名
    folder_name = driver.find_element(By.CLASS_NAME, "CoverPodcast-title").text
    global folder_path
    folder_path = os.path.join(output_path, clean_name(folder_name))
    os.makedirs(folder_path, exist_ok=True)

    # Store iframe web element
    buttons = driver.find_elements(By.CSS_SELECTOR, "button.Button.light.primary.small.circular.svelte-8vggd3")
    for button in buttons:

        title = str(button.get_attribute('aria-label'))

        if "Ep" in title:
            episode = re.search(r"Ep\s?\d", title).group()
            content = re.search(r'\s(.*) \|', title).group(1)
            title = episode + " " + content
        else:
            title = clean_name(title[8:])

        # js 点击
        driver.execute_script("arguments[0].click();", button)

        # 等待媒体文件加载
        time.sleep(5)

        # 找到包含音频元素的<div>元素
        div_element = driver.find_element(By.ID, 'player-wrapper')

        # 在<div>元素的范围内查找音频元素
        audio = div_element.find_element(By.TAG_NAME, 'audio')

        # 提取音频的src属性
        src = audio.get_attribute('src')
        print(title, src)
        # print(title)
        filename = title + re.search(r"\.\w{3}$", src).group()
        filename_src.append((filename, src))
        e.set()

        if test:
            break

    # 关闭浏览器窗口
    driver.quit()


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
    title = clean_name(driver.find_element(By.CSS_SELECTOR, 'a.font-bold.ln-l1-text.inline').text)

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
        while e.wait(timeout=30):
            e.clear()
            # threading.Thread(target=aria2c_downloader).start()
            executor.submit(aria2c_downloader)


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
                        help="for test")
    parser.add_argument('-t', "--test", action="store_true",
                        help="for test")

    args = parser.parse_args()
    e = threading.Event()
    lock = threading.Lock()
    main(args.link, args.output_path, args.parallel, args.test)
