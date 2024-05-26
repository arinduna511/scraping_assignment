from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import sys



input_file_path = 'scraping_assignment/input_list.csv'
output_file_path = 'scraping_assignment/scrapped_data.csv'


def format_date(string_date):
    date_list = string_date.split(' ')
    ordinals = ['st', 'nd', 'rd', 'th']
    for ordinal in ordinals:
        if ordinal in date_list[0]:
            date_list[0] = date_list[0].replace(ordinal, '')
            string_date = ' '.join(date_list)
    formatted_date = datetime.strptime(string_date, '%d %B %Y' ).strftime('%Y-%m-%d')
    return formatted_date


def save_scrapped_data(output_file_path, book_details):
    with open(output_file_path, mode='w', newline='') as output_file:
        fieldnames = book_details[0].keys()
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(book_details)
    print(f'Data saved to {output_file_path}')


def scrape_book_data(input_file_path):
    book_details = []
    try:
        # configuring webdriver
        chromedriver_path = 'scraping_assignment/chromedriver'
        options = Options()
        options.headless = True 
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        driver.implicitly_wait(5)

        with open(input_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            first_row = next(reader)        
            for row in reader:
                book_isbn = row[0]
                book = {}
                driver.get("https://www.booktopia.com.au/book/{}.html".format(book_isbn))
                driver.implicitly_wait(5)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                title = soup.find('h1').get_text()
                if 'The page you are trying to access no longer exists or has been moved.' in title:
                    book["Title"] = "Book Not Found"
                else:
                    author = soup.find('span', class_='MuiTypography-root MuiTypography-body1 mui-style-1plnxgp').text

                    # checking book availability and getting prices if available
                    p_text = soup.find('p', class_='MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom mui-style-5wrrjv')
                    if p_text:
                        rrp = ''
                        dp = ''
                    else:
                        dp = soup.find('p', class_='MuiTypography-root MuiTypography-body1 BuyBox_sale-price__PWbkg mui-style-tgrox').text
                        rrp_element = soup.select_one('span.strike')
                        if rrp_element:
                            rrp = rrp_element.text
                        else:
                            rrp = dp
                            dp = ''
                    
                    # finding all paragraph elements and extracting text to get other details
                    paragraphs = soup.find_all('p')
                    for paragraph in paragraphs:
                        if 'Format' in paragraph.get_text():
                            book_type = paragraph.get_text().split(':')[-1].strip()
                        if 'ISBN-10' in paragraph.get_text():
                            isbn_10 = paragraph.get_text().split(':')[-1].strip()
                        if 'Published:' in paragraph.get_text():
                            published = format_date(paragraph.get_text().split(':')[-1].strip())
                        if 'Publisher' in paragraph.get_text():
                            publisher = paragraph.get_text().split(':')[-1].strip()
                        if 'Number of Pages' in paragraph.get_text():
                            number_of_pages = paragraph.get_text().split(':')[-1].strip()
                    book["Title"] = title if title else ''
                    book["Author"] = author if author else ''
                    book["Book Type"] = book_type if book_type else ''
                    book["Original Price"] = rrp if rrp else ''
                    book["Discounted Price"] = dp if dp else ''
                    book["ISBN-10"] = isbn_10 if isbn_10 else ''
                    book["Published Date"] = published if published else ''
                    book["Publisher"] = publisher if publisher else ''
                    book["Number of Pages"] = number_of_pages if number_of_pages else ''
                    if book["Book Type"] == 'ePUB' or book["Book Type"] == 'E-Book':
                        book["Book Type"] = 'eBook'
                book_details.append(book)
        save_scrapped_data(output_file_path, book_details)
    except Exception as e:
        error_msg = e
        msg = 'Error on line no.: {}\n'.format(sys.exc_info()[-1].tb_lineno)+ 'type of error: {}  \n'.format(type(e).__name__)+ 'error_msg: {} '.format(error_msg)
        print(msg)
    finally:
        driver.quit()


if __name__ == '__main__':
    scrape_book_data(input_file_path)

