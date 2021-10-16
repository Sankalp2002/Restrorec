# from Reco.models import RecoUser,Restaurant,menuItem
# df_item= pd.read_csv('/static/datasets/all_items.csv')
# df_rest = pd.read_csv('/static/datasets/all_rest.csv')
# df_rest.columns = ['Name', 'Rating','Cuisine', 'Address', 'No. of Ratings']
# rest_list=df_rest.values.tolist()
# item_list=df_item.values.tolist()
# for each row in rest_list:
#     Restaurant.objects.get_or_create(name=row[0],rating=row[1],cuisine=row[2],address=row[3],totalRatings=row[4])
# for each row in item_list:
#     t=row[6]
#     menuItem.objects.get_or_create(category=row[0],name=row[1],price=row[2],description=row[3],diet=row[4],rating=row[5],restaurantId__id=t)