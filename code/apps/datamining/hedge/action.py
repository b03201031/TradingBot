from ....resources.api.rest import OKCoinFuture, OKCoinSpot
from ....resources.api import hedge as hedge_action

from ....resources.position import hedge as hedge_position
from ....resources.strategy.hedge import Hedge  as hedge_strategy

from ....test.verbose import vprint

import datetime
import time
import os
import configparser

import csv
import json

def start_mining(root_dir):


	setting_path = os.path.join(root_dir, 'config/setting.conf')
	trading_path = os.path.join(root_dir, 'config/apps/datamining/hedge.conf')
	
	
	#load setting
	setting_config = configparser.ConfigParser()

	setting_config.read(setting_path)
	
	URL = setting_config['URL']['okex']
	AUTH = dict(setting_config['AUTH'])


	#load trading config
	trading_config = configparser.ConfigParser()
	
	trading_config.read(trading_path)
	vprint('(trading)load trading config')

	SpotOrderConfig = dict(trading_config['SpotAPI'])
	FutureOrderConfig = dict(trading_config['FutureAPI'])
	#StrategyConfig = dict(trading_config['Strategy'])
	
	
	spot_api = OKCoinSpot(AUTH, URL, SpotOrderConfig)
	future_api = OKCoinFuture(AUTH, URL, FutureOrderConfig)

	start = datetime.datetime(2018, 12, 25)
	end = start + datetime.timedelta(minutes=1)
	r = future_api.get_market_data(start, end)
	print(r.json())
	#declare managers

	
	#strategy = hedge_strategy(config=StrategyConfig)

def start_new_file(start_datetime, file_path, spot_api, future_api):


	with open(file_path, 'w', newline='') as csvfile:
		fieldnames = ['time', 'spot_open', 'spot_close', 'spot_high', 'spot_low', 'spot_vol', 'future_open', 'future_close']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		start =  start_datetime
		while True:
			end = start + datetime.timedelta(minutes=1, seconds=0, microseconds=0)
			data_spot = spot_api.get_market_data(start, end)
			start = end
			data_spot = dict(data_spot.json()[0])
			
			'''
			data_spot['spot_open'] = data_spot.pop('open')
			data_spot['spot_close'] = data_spot.pop('close')
			data_spot['spot_high'] = data_spot.pop('high')
			data_spot['spot_low'] = data_spot.pop('low')
			data_spot['spot_vol'] = data_spot.pop('volume')
			
			writer.writerow(data_spot)
			'''
			time.sleep(1)

