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
from Reco.models import RecoUser,Restaurant,menuItem
from Reco.forms import restForm,userRegisterFormA,userRegisterFormB
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.core.validators import ValidationError,validate_email
# from django.conf import settings
# from settings import STATIC_DIR
# Create your views here.


def preprocessing(selected_dish):
    nltk.download('stopwords')
    all_rest=Restaurant.objects.all()
    all_item=menuItem.objects.all()
    all_items=[]
    all_rests=[]
    for r in all_rest:
        t=[r.name,r.rating,r.cuisine,r.address,r.totalRatings]
        all_rests.append(t)
    for r in all_item:
        t=[r.category,r.name,r.price,r.description,r.diet,r.rating,r.restaurantId_id]
        all_items.append(t)

    df=pd.DataFrame(all_items,columns=['Category', 'Item Name','Price','Description','Veg/Non-veg','Rating','Restaurant Index'])
    df_rest=pd.DataFrame(all_rests,columns=['Name', 'Rating', 'Cuisine', 'Address', 'No. of Ratings'])
    print(df.dtypes)
    print(df_rest.dtypes)
    df['Description'] = df['Description'].str.lower()
    df['Description'] = df['Description'].apply(  # removing punctuation with empty string
        lambda text: text.translate(str.maketrans('', '', string.punctuation)))

    STOPWORDS = set(stopwords.words('english'))  # loading stopwords of english
    df['Description'] = df['Description'].apply(lambda text: " ".join(  # remving stopwords from description
        [word for word in str(text).split() if word not in STOPWORDS]))

    tfidf = TfidfVectorizer(analyzer='word', ngram_range=(
    1, 2), min_df=0, stop_words='english')
    # vectorise the description and calculate tfidf values
    tfidf_matrix = tfidf.fit_transform(df['Description'])

    # calculte correlation matrix of cosine similarity on the basis of tf idf
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

    rdishes = list()               # recommended dishes list

    idx = selected_dish  # getting index number of row

    score_series = pd.Series(cosine_similarities[idx]).sort_values(
        ascending=False)  # retriving values with maximum cosine similarity on the basis of index

    # indices of top 30  dishes
    # first position will be for dishes itself
    top10 = list(score_series.iloc[1:31].index)

    # print(top10)
    ntop10 = []

    for each in top10:
        if(each != idx):
            # appending tuple of (item name,restaurant index) to rdishes
            if (df.iloc[each, [1]][0], df.iloc[each, [6]][0]) not in rdishes:
                rdishes.append((df.iloc[each, [1]][0], df.iloc[each, [6]][0]))
                ntop10.append(each)

    # st.write(ntop10)
    # retrieving veg/nonveg of recommended list
    rveg = df.iloc[idx, [4]][0]

    # retrieving category of recommended list
    rcat = df.iloc[idx, [0]][0]
    rprice = df.iloc[idx, [2]][0]
    score = list()
    for nindex in ntop10:
        # retriving veg/nonveg of dish
        veg = df.iloc[nindex, [4]][0]
        # retriving category of dish
        cat = df.iloc[nindex, [0]][0]
        tempscore = 0
        if(veg == rveg):                                           # adding 3 if veg/nonveg matches
            tempscore = tempscore + 3
        if(rcat == cat):
            # adding 1 if category matches
            tempscore = tempscore + 1
        temprating = df.iloc[nindex, [5]][0]
        tempprice = df.iloc[nindex, [2]][0]

        # assigning score on the basis of rating
        tempscore = tempscore + 1.2*(temprating/5)
        normprice = (tempprice/830)
        # penalise on the basis of price
        tempscore = tempscore - 1.05*abs(normprice-rprice)/rprice

        score.append(tempscore)

    # sorting on the basis of score
    rdishes = [x for _, x in sorted(zip(score, rdishes), reverse=True)]
    # sorting dish indices on the basis of score
    ntop10 = [x for _, x in sorted(zip(score, ntop10), reverse=True)]

    dishname = []

    newname = []
    newridshes = []
    newntop10 = []


    # loop to retrieve dishname
    for dish in rdishes:
        dishname.append(dish[0])

    i = 0

    # loop to append dishes if frequency is 3
    for name in dishname:
        if(newname.count(name) <= 2):
            newname.append(name)
            newridshes.append(rdishes[i])
            newntop10.append(ntop10[i])
        i = i+1


    rdishes = newridshes[0:10]  # taking top 10 dishes
    ntop10 = newntop10[0:10]
    # st.write(rdishes)
    rindex = []  # list for restaurant index

    for dish in rdishes:  # appending restaurant index of dish
        rindex.append(dish[1])

    print(rindex)

    dishes_details = []
    i = 0
    for index in rindex:
        templist = []
        templist.append(rdishes[i][0])  # dishname
        templist.append(df.iloc[ntop10[i], [0]][0])
        templist.append(df.iloc[ntop10[i], [2]][0])
        # # Restaurant name
        templist.append(df_rest.iat[index-1,0])
        templist.append(df_rest.iat[index-1,1])
        templist.append(df_rest.iat[index-1,2])
        templist.append(df_rest.iat[index-1,3])

        i = i+1
        print(templist)
        dishes_details.append(templist)

    
    
    return dishes_details

@login_required
def showRest(request):
    if request.method == 'POST':
        d=request.POST.get("restaurant")
        menu=menuItem.objects.filter(restaurantId=d)
        return render(request, 'main2.html',{'menu':menu})
    else:
        rest=Restaurant.objects.all()
        return render(request, 'main.html',{'rest':rest})

@login_required
def showMenu(request):
    if request.method == 'POST':
        d=int(request.POST.get("restaurant"))
        dishes=preprocessing(d-1)
        return render(request, 'display.html',{'dishes':dishes})
    else:
        # all_rest=list(Restaurant.objects.all())
        form=restForm()
        return render(request, 'main.html',{'form':form})

def registerView(request):
    registered=False
    if request.method=='POST':
        formA=userRegisterFormA(data=request.POST)
        formB=userRegisterFormB(data=request.POST)
        if formA.is_valid() and formB.is_valid():
            docA=formA.save(commit=False)
            #print(formB.cleaned_data['username'])
            docA.set_password(docA.password)
            docA.save()
            docB=formB.save(commit=False)
            docB.RUser=docA
            docB.save()
            registered=True
            m="Registration Successful"
            return HttpResponseRedirect(reverse('Reco:loginView'))
        else:
            print(userRegisterFormA.errors,userRegisterFormB.errors)
    else:
        formA=userRegisterFormA()
        formB=userRegisterFormB()
        return render(request, 'register.html',{'formA':formA,'formB':formB})

def loginView(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        docuser=authenticate(username=username,password=password)
        if docuser:
            if docuser.is_active and docuser.is_superuser:
                return(HttpResponse("Invalid login details!"))
                # login(request,docuser)
                # return HttpResponseRedirect(reverse('Blood:adminpanel'))
            elif docuser.is_active:
                login(request,docuser)
                return HttpResponseRedirect(reverse('Reco:showRest'))
            else:
                return HttpResponse("Account not active")
        else:
            print("A login failed")
            return(HttpResponse("Invalid login details!"))
    else:
        return render(request, 'login.html',)