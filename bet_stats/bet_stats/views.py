import pandas as pd
from django.db import connection
from django.http import HttpResponse


def get_data(request):

	df = pd.read_json('http://ec2-54-218-243-73.us-west-2.compute.amazonaws.com/api/completed?sport=mlb')
	#df.(con=connection, name='raw_data', schema='jblackwell', index=False, if_exists='replace')
	return HttpResponse(df.to_json())