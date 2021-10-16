from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
import re
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.corpus import stopwords
import re
import numpy as np
import pandas as pd
# from django.conf import settings
# from settings import STATIC_DIR
# Create your views here.


def preprocessing():
    nltk.download('stopwords')
    df = pd.read_csv('../RESTROREC/static/datasets/all_items.csv')
    df_rest = pd.read_csv('../RESTROREC/static/datasets/all_rest.csv')
    df_rest.columns = ['Name', 'Rating',
                       'Cuisine', 'Address', 'No. of Ratings']
    df.drop_duplicates(inplace=True)  # remove any duplicates
    df['Description'] = df['Description'].str.lower()
    df['Description'] = df['Description'].apply(  # removing punctuation with empty string
        lambda text: text.translate(str.maketrans('', '', string.punctuation)))

    STOPWORDS = set(stopwords.words('english'))  # loading stopwords of english
    df['Description'] = df['Description'].apply(lambda text: " ".join(  # remving stopwords from description
        [word for word in str(text).split() if word not in STOPWORDS]))
    lists={"item":df.values.tolist(),"rest":df_rest.values.tolist()}
    return lists


def showMenus(request):
    lists=preprocessing()
    if request.method == 'POST':
        return render(request, 'main.html')
    else:
        return render(request, 'main.html',lists)


