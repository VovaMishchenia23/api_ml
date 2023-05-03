import pickle

from bs4 import BeautifulSoup
from datetime import date, timedelta
import calendar
import requests
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import os
from dotenv import load_dotenv

# loading environmental variables
load_dotenv()

# loading stopwords list 
nltk.download('stopwords')

URL_BASE = os.getenv("ISW_URL")
YEAR = "2023"
DATA_FOLDER = "data/"

# file with vectorizer to vectorize new isw report based on the 330 old reports
VECTORIZER_FILE = "vectorizer.pkl"


def get_last_isw():
    html = get_html()
    main_text = parse_text(html)
    clean_text = clear_text(main_text)
    stemm_text = stemming(clean_text)
    return stemm_text

# get last isw report raw html page 
def get_html():
    report_date = date.today() - timedelta(1)
    url = create_url(report_date)
    req = requests.get(url)
    while req.status_code != 200:
        report_date -= timedelta(1)
        new_url = create_url(report_date)
        req = requests.get(new_url)
    return req.text

# create url for getting latest isw report
def create_url(date_):
    return f"{URL_BASE}russian-offensive-campaign-assessment-{calendar.month_name[date_.month].lower()}-{date_.day}-{YEAR}"


def parse_text(html):
    bs = BeautifulSoup(html, "html.parser")
    main_div = bs.find_all("div", {"class": "field-type-text-with-summary"})[0]
    # deleting all tags
    main_div = re.sub(r"<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>", "", main_div.text)
    # deleting all links
    main_div = re.sub(r"(https|http|ttp)(\S+.*\s)", "", main_div)
    # deleting all numbers like [12]
    main_div = re.sub(r"\[\d*\]", "", main_div)
    return main_div


# remove all line without dot(first lines with authors names and date and also image signature)
# remove sentences with words Click and Note
def suitable_string(string):
    return len(string.strip()) != 0 and "Click" not in string \
           and "Note" not in string and "." in string and "W." not in string

# get date in format of isw report to delete it from the text
def get_date(date):
    date = date.split("-")
    return " " + calendar.month_name[int(date[1])].capitalize() + " " + str(int(date[2]))


# remove mention repost date
def remove_date(data, date):
    return re.sub(get_date(date), "", data)


def clear_text(data):
    text = ""
    for line in data.split("\n"):
        if suitable_string(line):
            line = line.strip().lower()
            # remove punctuations
            line = line.translate(data.maketrans(' ', ' ', ',:!.();“”~@?\"[]*/_‘{}–=$#%&"“”—'))

            line = line.replace("-", " ")
            # remove all digits
            line = re.sub(r"[\d]", "", line)

            # remove stopwords
            stopwords_ = stopwords.words("english")
            stopwords_.extend(["th", "st", "nd", "pm", "hours", "hour", "km", "m", "meters", "kilometers", "am", "e"])
            for word in line.split():
                if word not in stopwords_:
                    text += word + " "

            # remove copyright sign
            text = re.sub(r"©", "", text)

            # remove extra spaces
            text = text.replace("  ", " ")

    return text

# stemming the text by PorterStemmer
def stemming(data):
    stemmer = PorterStemmer()
    new_data = ""
    for word in data.split(" "):
        new_data += stemmer.stem(word) + " "
    return new_data

# convert text to tf-idf matrix based on the 330 old isw reports
def get_last_isw_matrix():
    with open(f"{DATA_FOLDER}{VECTORIZER_FILE}", "rb") as file:
        vectorizer = pickle.load(file)
    tf_idf = vectorizer.transform([get_last_isw()])
    return tf_idf


if __name__ == "__main__":
    get_last_isw()
