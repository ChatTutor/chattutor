import os
import time
from urllib.error import URLError
from urllib.parse import urljoin

import arxiv
import requests
from bs4 import BeautifulSoup
from google.cloud import storage
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up Options for Chrome
# chrome_options = Options()
# chrome_options.add_argument('--headless')  # Run browser in the background
# chrome_options.add_argument('--disable-gpu')  # Applicable to windows os only
# chrome_options.add_argument('start-maximized')
# chrome_options.add_argument('disable-infobars')
# chrome_options.add_argument('--disable-extensions')
# driver = webdriver.Chrome(options=chrome_options)
# # driver = webdriver.Chrome()

# # URL of the website to scrape
# url = 'https://cqn-erc.org/research/research-feed/'
# driver.get(url)

# arxiv_ids = []
# try:
#     # Keep clicking "Load more" until all the articles are on the page
#     x=0
#     while True:
#         try:
#             time.sleep(0.1)
#             button_path = '//*[@id="feed-heading"]/div[5]/div/a'
#             load_more_button = WebDriverWait(driver, 5).until(
#               EC.presence_of_element_located((By.XPATH, button_path))
#             )
#             print(load_more_button)
#             load_more_button.click()
#             x+=1
#             print(x)
#         except (TimeoutException, StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException):
#             print('no more "load more" buttons found')
#             break

#     # Get a list of all "View Article" buttons
#     try:
#         article_number = 1
#         view_article_buttons = []
#         while True:
#           button_path = f'//*[@id="feed-heading"]/div[2]/div[{article_number}]/div[2]/a'
#           view_article_button = driver.find_element(By.XPATH, button_path)
#           view_article_buttons.append(view_article_button)
#           print(article_number)
#           article_number += 1
#     except (NoSuchElementException, ElementClickInterceptedException):
#         print('no more "view article" buttons found')

#     # Click on each "View Article" button and retrieve the arXiv ID
#     for i,button in enumerate(view_article_buttons):
#       button.send_keys(Keys.COMMAND + Keys.RETURN)

#       # Switch to the new tab
#       WebDriverWait(driver, 15).until(EC.number_of_windows_to_be(2))
#       driver.switch_to.window(driver.window_handles[1])

#       # Get the arXiv ID
#       arxiv_button_path = '//*[@id="page-wrapper"]/main/div/div[1]/article/div[3]/a[1]'
#       arxiv_class_selector = '.button.outline'
#       print(f'getting ID for article #{i}')
#       arxiv_button = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, arxiv_class_selector))
#       )
#       arxiv_url = arxiv_button.get_attribute('href').split('/')[-1]
#       arxiv_ids.append(arxiv_url)

#       # Close the current tab and switch back to the main window
#       driver.close()
#       driver.switch_to.window(driver.window_handles[0])
# finally:
#     driver.quit()

# # Save the scraped IDs
# with open('arxiv_ids.txt', 'w') as file:
#     for link in arxiv_ids:
#         file.write(link + '\n')

# print("ArXiv links are saved in arxiv_ids.txt.")


def upload_blob(bucket_name: str, file_content: str, destination_blob_name: str) -> None:
    """
    Uploads a file to the bucket.
    bucket_name = "your-bucket-name"
    source_file_name = "local/path/to/file"
    destination_blob_name = "storage-object-name"
    """

    # Initialize a storage client using your service account key file.
    storage_client = storage.Client.from_service_account_json(
        "chattutor-393319-5c666d5a8c61.json"
    )
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(file_content)

    print(f"File uploaded as {destination_blob_name}.")


def file_exists_in_bucket(bucket_name: str, blob_name: str) -> bool:
    """
    Checks if a file exists in the specified bucket.
    """
    storage_client = storage.Client.from_service_account_json(
        "chattutor-393319-5c666d5a8c61.json"
    )
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()


bucket_name = "downloaded_content"  # replace with your bucket name

# Read the links from the file
with open("arxiv_ids.txt", "r") as file:
    links = file.readlines()

max_retries = 3
delay_between_requests = 2
for link in links:
    retries = 0
    success = False

    while retries < max_retries and not success:
        try:
            paper = next(arxiv.Search(id_list=[link]).results())
            print(f"Downloading {link}: {paper}")

            blob_name = f"{paper.title}.pdf"

            if file_exists_in_bucket(bucket_name, blob_name):
                print(f"{blob_name} already exists in the bucket. Skipping...")
                success = True
                continue

            response = requests.get(paper.pdf_url)
            if response.status_code == 200:
                upload_blob(bucket_name, response.content, f"{paper.title}.pdf")
                success = True
                print(f"Downloaded and uploaded {link}")
            else:
                print(f"Failed to download {link}")

        except URLError as e:
            print(f"URLError for {link}: {e}. Retrying...")
            retries += 1
            time.sleep(delay_between_requests)

        # except Exception as e:  # Catch other exceptions and be explicit about variable 'e'
        #     print(f"Error processing {link}: {e}")
        #     retries += 1  # Depending on the type of error, you may want to decide whether to retry or not.
        #     time.sleep(delay_between_requests)  # Same here, decide based on the error if a sleep is necessary.


### Used for downloading files locally
# for link in links:
#   paper = next(arxiv.Search(id_list=[link]).results())
#   paper.download_pdf(dirpath="./downloaded_papers", filename=f"{paper.title}.pdf")

# delay_between_requests = 2  # in seconds
# max_retries = 3  # Maximum number of retries for each request
# downloaded_paper_dir = "./downloaded_papers"
# for link in links:
#   retries = 0
#   success = False

#   while retries < max_retries and not success:
#     try:
#       paper = next(arxiv.Search(id_list=[link]).results())
#       print(f'Downloading {link}: {paper}')
#       if paper.title not in os.listdir(downloaded_paper_dir):
#         paper.download_pdf(dirpath=downloaded_paper_dir, filename=f"{paper.title}.pdf")
#         success = True
#         print(f"Downloaded {link}")

#     except URLError as e:
#           if isinstance(e.reason, ConnectionResetError):
#               print(f"ConnectionResetError for {link}: {e.reason}. Retrying...")
#           else:
#               print(f"URLError for {link}: {e}. Retrying...")
#           retries += 1
#           time.sleep(delay_between_requests)

#     except Exception as e:  # Catch other exceptions and be explicit about variable 'e'
#         print(f"Error processing {link}: {e}")
#         retries += 1  # Depending on the type of error, you may want to decide whether to retry or not.
#         time.sleep(delay_between_requests)  # Same here, decide based on the error if a sleep is necessary.
