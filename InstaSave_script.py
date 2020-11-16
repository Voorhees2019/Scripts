from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import os
import requests
from tqdm import tqdm
from enum import Enum
import re


class FileType(Enum):
    PHOTO = 1
    VIDEO = 2
    PROFILE_PICTURE = 3


def connection_to_internet(url='http://www.google.com/', timeout=5):
    """ Function to check the Internet connection """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        print('[START] You\'re connected to the Internet')
        return True
    except requests.HTTPError as err:
        print(f'[ERROR] Checking your Internet connection has failed, status code = {err.response.status_code}')
    except requests.ConnectionError:
        print('[ERROR] There is no Internet connection')
        return False


def download_profile_picture(url):

    """ Function to download a profile picture from Instagram profile """

    insta_url_pattern = re.compile(r"(https://www\.)?instagram\.com/.*\?hl=[a-z]{2,5}")

    if match := re.match(insta_url_pattern, url):
        url = re.sub(r'\?hl=[a-z]{2,5}', '?__a=1', match.group())
    else:
        url += '?__a=1'

    response = requests.get(url)
    content = response.content.decode()
    if response.status_code == 200:
        try:
            profile_picture_url = re.search(r'profile_pic_url_hd\":\"([^\"\']+)', content).group()
        except AttributeError:
            print(f'[ERROR] Inappropriate link was provided for the chosen file type. Try again')
            return
        image_url = re.sub(r'profile_pic_url_hd":"', '', profile_picture_url)
        return image_url
    else:
        print(f'[ERROR] Status code = {response.status_code}')


def download_single_file(url, file_type=FileType.PHOTO, dest_path='D:\\Voorhees\\InstaSave'):

    """ Function to download a single file from Instagram """

    not_profile_url_pattern = re.compile(r"^(https://www\.)?instagram\.com/?$")
    not_insta_url_pattern = re.compile(r"(https://www\.)?instagram\.com/.+")

    if re.match(not_profile_url_pattern, url):
        print('[ERROR] Enter the link related to a profile')
        return
    elif not re.match(not_insta_url_pattern, url):
        print(f'[ERROR] Inappropriate link, must be like https://www.instagram.com/*****')
        return
    elif not url.startswith('https'):
        url = 'https://www.' + url

    try:
        f = urllib.request.urlopen(url)
    except ValueError:
        print('[ERROR] Invalid link. Try again')
        return
    except urllib.error.HTTPError as http_err:
        print(f'[ERROR] {http_err}')
        return

    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    if file_type == FileType.PHOTO:
        meta_tag = soup.find_all('meta', {'property': 'og:image'})
    elif file_type == FileType.VIDEO:
        meta_tag = soup.find_all('meta', {'property': 'og:video'})
    else:
        meta_tag = None

    try:
        if meta_tag:
            image_url = meta_tag[0]['content']
        else:
            image_url = download_profile_picture(url)

        if image_url is None:
            return
    except IndexError:
        print('[ERROR] Inappropriate link was provided for the chosen file type. Try again')
        return

    dest_file_name = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    if file_type == FileType.PHOTO or file_type == FileType.PROFILE_PICTURE:
        dest_file_name += '.jpg'
    elif file_type == FileType.VIDEO:
        dest_file_name += '.mp4'

    # simple downloading without a progress bar. Uncomment two next lines and comment the progress bar code below
    # dest_file_name = os.path.join(dest_path, dest_file_name)
    # urllib.request.urlretrieve(image_url, dest_file_name)

    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='b', unit_scale=True, desc=dest_file_name)
        dest_file_name = os.path.join(dest_path, dest_file_name)

        with open(dest_file_name, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print(f'[ERROR] something went wrong')

        return True
    else:
        print(f'[ERROR] Status code = {response.status_code}')


if __name__ == '__main__':

    input_to_filetype = {
        1: FileType.PHOTO,
        2: FileType.VIDEO,
        3: FileType.PROFILE_PICTURE
    }

    if connection_to_internet():
        try:
            print('What do you want to download from Instagram:\n'
                  '1 - Photo\n2 - Video\n3 - Profile Picture\nEnter a file type number:')
            while True:
                try:
                    type_input = input()
                    type_input = int(type_input)

                    file_type = input_to_filetype[type_input]
                    break
                except ValueError:
                    print(f'[ERROR] Undefined file type. Must be an integer from 1 to 3, got "{type_input}"')
                    continue
                except KeyError:
                    print(f'[ERROR] Undefined file type. Must be an integer from 1 to 3, got "{type_input}"')
                    continue

            while True:
                url = input('Enter the URL:')
                if download_single_file(url, file_type):
                    break
                else:
                    continue

        except KeyboardInterrupt:
            print('[EXIT] Keyboard interruption')
