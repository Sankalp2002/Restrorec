from django.shortcuts import render
from django.urls import reverse,reverse_lazy
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
from Reco.forms import userRegisterFormA,userRegisterFormB
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.core.validators import ValidationError,validate_email
# from django.conf import settings
# from settings import STATIC_DIR
# Create your views here.
def initial():
    df_item= pd.read_csv('../RESTROREC/static/datasets/all_items.csv')
    df_rest = pd.read_csv('../RESTROREC/static/datasets/all_rest.csv')
    df_rest.columns = ['Name', 'Rating','Cuisine', 'Address', 'No. of Ratings']
    rest_list=df_rest.values.tolist()
    item_list=df_item.values.tolist()

    for row in rest_list:
        Restaurant.objects.get_or_create(name=row[0],rating=row[1],cuisine=row[2],address=row[3],totalRatings=row[4])

    for row in item_list:
        t=row[6]
        if t<24:
            menuItem.objects.get_or_create(category=row[0],name=row[1],price=row[2],description=row[3],diet=row[4],rating=row[5],restaurantId_id=t)
        else:
            menuItem.objects.get_or_create(category=row[0],name=row[1],price=row[2],description=row[3],diet=row[4],rating=row[5],restaurantId_id=t-1)

def foodfun(fname):
    df= pd.read_csv('../RESTROREC/static/datasets/indian_food2.csv')
    food=[fname,-1,-1,-1,-1,-1]
    df.loc[len(df)] = food
    df['name'] = df['name'].str.lower()              #lower chars
    df['name'] = df['name'].apply( lambda text: text.translate(str.maketrans('', '', string.punctuation)))
    STOPWORDS = set(stopwords.words('english'))  # loading stopwords of english
    df['name'] = df['name'].apply(lambda text: " ".join([word for word in str(text).split() if word not in STOPWORDS]))

    tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['name'])                #vectorise the description and calculate tfidf values

    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)      
    idx=len(df)-1

    score_series = pd.Series(cosine_similarities[idx]).sort_values(
        ascending=False)  # retriving values with maximum cosine similarity on the basis of index

    top_index = list(score_series.iloc[1:2].index)[0]
    top_score=list(score_series.iloc[1:2])[0]

    if top_score>=0.5:
        return top_index
    else:
        return -1

def getUser(request):
    u = request.user
    uid=u.id
    ru=RecoUser.objects.get(RUser_id=uid)
    # print(type(ru.ingredient))
    # print(type(ru.diet))
    # type(ru.ingredient)
    desc=[ru.ingredient,ru.diet,ru.flavour,ru.state,ru.region]
    return desc

def model1(selected_dish):
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

def model2(selected_dish,request):
    df_food= pd.read_csv('../RESTROREC/static/datasets/indian_food2.csv')
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
    # print(df.dtypes)
    # print(df_rest.dtypes)
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
    top10 = list(score_series.iloc[1:100].index)

    # print(top10)
    ntop10 = []

    for each in top10:
        if(each != idx):
            # appending tuple of (item name,restaurant index) to rdishes
            if (df.iloc[each, [1]][0], df.iloc[each, [6]][0]) not in rdishes:
                rdishes.append((df.iloc[each, [1]][0], df.iloc[each, [6]][0],each))
                ntop10.append(each)

    # st.write(ntop10)
    # retrieving veg/nonveg of recommended list
    rveg = df.iloc[idx, [4]][0]

    # retrieving category of recommended list
    rcat = df.iloc[idx, [0]][0]
    rprice = df.iloc[idx, [2]][0]
    score = list()
    for nindex in ntop10:
        tempscore = 0
        top_index=foodfun(df.iloc[nindex,[1]][0])
        if top_index!=-1:
            user=getUser(request)
            user=[f.lower() for f in user]
            food=list(df_food.iloc[top_index])
            # print(food)
            # print(type(food[0]))
            # print(type(food[1]))
            # print(type(food[2]))
            # print(type(food[3]))
            # print(type(food[4]))
            food=[f.lower() for f in food]
            if food[5]==user[4]:
                tempscore= tempscore + 5
            if food[4]==user[3]:
                tempscore= tempscore + 5
            if food[3]==user[2]:
                tempscore= tempscore + 5
            if food[2][0:3]==user[1][0:3]:
                tempscore= tempscore + 5
            fing= food[1].split(', ')
            uing= user[0].split(',')
            for u in uing:
                if u in fing:
                    tempscore=tempscore+5
        # retriving veg/nonveg of dish
        veg = df.iloc[nindex, [4]][0]
        # retriving category of dish
        cat = df.iloc[nindex, [0]][0]
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
        if(newname.count(name) < 2):
            newname.append(name)
            newridshes.append(rdishes[i])
            newntop10.append(ntop10[i])
        i = i+1


    rdishes = newridshes[0:10]  # taking top 10 dishes
    ntop10 = newntop10[0:10]
    # st.write(rdishes)
    rindex = []  # list for restaurant index
    dindex = []
    for dish in rdishes:  # appending restaurant index of dish
        rindex.append(dish[1])
        dindex.append(dish[2])

    print(rindex)

    dishes_details = []
    i = 0
    for j in range(len(rindex)):
        index=rindex[j]
        templist = []
        templist.append(rdishes[i][0])  # dishname
        templist.append(df.iloc[ntop10[i], [0]][0])
        templist.append(df.iloc[ntop10[i], [2]][0])
        # # Restaurant name
        templist.append(df_rest.iat[index-1,0])
        templist.append(df_rest.iat[index-1,1])
        templist.append(df_rest.iat[index-1,2])
        templist.append(df_rest.iat[index-1,3])
        templist.append(dindex[j]+1)
        templist.append(df.iloc[ntop10[i], [5]][0])
        print(dindex[j]+1)
        i = i+1
        #print(templist)
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
        #dishes=model1(d-1)
        dishes=model2(d-1,request)
        return render(request, 'display.html',{'dishes':dishes,'User':request.user})
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
            return HttpResponseRedirect(reverse('loginView'))
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


@login_required
def profileView(request):
    u = request.user
    uid=u.id
    ru=RecoUser.objects.get(RUser_id=uid)
    #ing=ru.ingredient
    return render(request, 'myprofile.html',{'User':ru})

@login_required
def orderView(request):
    if request.method == 'POST':
        itemIds=request.POST.getlist('order')
        orders=[]
        for id in itemIds:
            name=menuItem.objects.get(itemId=id).name
            price=menuItem.objects.get(itemId=id).price
            resto=menuItem.objects.get(itemId=id).restaurantId
            orders.append([name,price,resto,id])
        return render(request, 'rateFood.html',{'orders':orders})
    else:
        # form=ratingForm()
        return render(request, 'rateFood.html')

@login_required
def rateView(request):
    if request.method == 'POST':
        orderIds=request.POST.getlist('ids')
        ratings=request.POST.getlist('ratings')
        # print(orderIds)
        # print(ratings)
        for i in range(len(orderIds)):
            id=orderIds[i]
            item=menuItem.objects.get(itemId=id)
            item.rating=ratings[i]
            item.save()
        return HttpResponseRedirect(reverse('Reco:showRest'))
    else:
        return render(request, 'rateFood.html',)

@login_required
def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('loginView'))


def errorview(request,pid):
    e="You are not logged in!"
    return render(request,'error.html',{'e':e})

def error_404(request, exception):
   context = {}
   return render(request,'404.html', context)