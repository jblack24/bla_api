import pandas as pd
import os
import numpy as np
from django.db import connection
from django.http import HttpResponse
import json


def get_data(request):

	df = pd.read_json('http://ec2-54-218-243-73.us-west-2.compute.amazonaws.com/api/completed?sport=mlb')

	#daily totals overall
	df_date=df[['game_date', 'result', 'units']].groupby('game_date').agg(total_bets=('result', 'count'), total_units=('units', 'sum'))

	#Daily totals by W/L/P
	df_date_res=df[['game_date', 'result', 'units', 'market_units', 'closing_units']].groupby(['game_date', 'result']).agg(daily_bets=('result','count'), daily_units=('units','sum'))
	df_market_closing=df[['game_date', 'result', 'units', 'market_units', 'closing_units']].groupby(['game_date']).agg(closing_units=('closing_units','sum'), market_units=('market_units', 'sum'))
	df_date_res=df_date_res.reset_index()

	#geting no action dataframe
	na=df_date_res.loc[df_date_res['result'].eq('NA')]

	dfl_temp=df_date_res.loc[df_date_res['result'].eq('L')]
	dfw_temp=df_date_res.loc[df_date_res['result'].eq('W')]
	dfp_temp=df_date_res.loc[df_date_res['result'].eq('P')]
	dfna_temp=df_date_res.loc[df_date_res['result'].eq('NA')]
	
	#Getting w, l, p stats
	dfl_temp.rename(columns={'daily_bets': 'l_daily_bets'}, inplace=True)
	dfl_temp.rename(columns={'daily_units': 'l_daily_units'}, inplace=True)
	
	dfw_temp.rename(columns={'daily_bets': 'w_daily_bets'}, inplace=True)
	dfw_temp.rename(columns={'daily_units': 'w_daily_units'}, inplace=True)


	dfp_temp.rename(columns={'daily_bets': 'p_daily_bets'}, inplace=True)
	dfp_temp.rename(columns={'daily_units': 'p_daily_units'}, inplace=True)

	dfna_temp.rename(columns={'daily_bets': 'na_daily_bets'}, inplace=True)
	dfna_temp.rename(columns={'daily_units': 'na_daily_units'}, inplace=True)

	df_temp=pd.merge(dfl_temp[['game_date','l_daily_bets', 'l_daily_units']],dfw_temp[['game_date','w_daily_bets', 'w_daily_units']], how='outer', on=['game_date'])
	df_temp=df_temp.merge(dfp_temp[['game_date', 'p_daily_bets', 'p_daily_units']], on=['game_date'], how='outer')
	df_temp=df_temp.merge(dfna_temp[['game_date', 'na_daily_units', 'na_daily_bets']], on=['game_date'], how='outer')

	#Getting cumulative stats
	cumulative_json={
					'overall':'overall',
					'cumulative_units':str('%+.2f' % df_date['total_units'].sum()), 
					'best_cumulative_units': str('%+.2f' % df_date['total_units'].sum()) , 
					'market_cumulative_units':str('%+.2f' % df_market_closing['market_units'].sum()), 
					'closing_cumulative_units':str('%+.2f' % df_market_closing['closing_units'].sum())
					}
	
	#Combining w,l,p,na with daily stats
	df_final=pd.merge(df_temp, df_date, on =['game_date'], how='outer')
	df_final=df_final.reset_index().rename(columns={'index': 'id'})
	df_final.index.set_names(['id'], inplace=True)
	df_final.fillna(0, inplace=True)
	merge_json=json.loads(df_final.to_json(orient='records'))
	
	#Prepending the overall stats
	merge_json= [cumulative_json]+merge_json

	return HttpResponse(json.dumps(merge_json),content_type="application/json")

#def calculate_best(df):

def push_data_to_db(df):
	df.to_sql(con=connection, schema=os.environ.get('DB_SCHEMA'))