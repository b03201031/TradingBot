import json
import time
from math import floor

from ...test.verbose import vprint 


class Manager:
	def __init__(self, **kwargs):
		self._spot_api = kwargs['spot_api']
		self._future_api = kwargs['future_api']
		self._manager_config = kwargs['config']
	#check the order filled if not filled cancel
	def check_future_filled(self, **kwargs):
		vprint('check future filled')
		order_id = kwargs['order_id']
		future_api = self._future_api
		r = future_api.find_order(order_id).json()
		if r['status'] == '2':
			vprint('future order filled')
			price = float(r['price'])
			fiat_amount = float(r['size'])*10.
			#per size = 10USD
			crypt_amount = round((fiat_amount)/price, 8)
			
			detail = {
				'fiat_amount': fiat_amount,
				'order_id': order_id,
				'price': price,
				'crypt_amount': crypt_amount,
			}

			vprint('price: ', price, ' crypt amount: ', crypt_amount, 'fiat amount: ', fiat_amount)

			return detail
		else:
			vprint('not filled yet')
			vprint('cancel future order')

			r = future_api.cancel_order(order_id).json()


			return False

	#check the order filled wait until filled
	def check_margin_filled(self, **kwargs):
		vprint('check margin filled')
		order_id = kwargs['order_id']
		spot_api = self._spot_api

		r = spot_api.find_order(order_id).json()
		if r['status'] == 'filled':
			vprint('margin order filled')
			filled_notional = float(r['filled_notional'])
			crypt_amount = float(r['filled_size'])
			price = floor((filled_notional/crypt_amount)*10000.)/10000.
			
			
			detail = {
				'order_id' : order_id,
				'price' : price,
				'crypt_amount': crypt_amount,
				'fiat_amount': filled_notional,
			}

			vprint('price: ', price, ' crypt amount: ', crypt_amount, 'fiat amount: ', filled_notional)

			return detail

		else:
			time.sleep(0.2)
			vprint('not filled yet')
			return self.check_margin_filled(**kwargs)


	def future_transaction(self, **kwargs):
		future_api = self._future_api
		order_args = kwargs['order_args']
		
		vprint('\nplace future order')
		r = future_api.place_order(**order_args).json()
		

		#fail place again
		if str(r['order_id']) == '-1':
			vprint('palce future order failed')
			return False
		else:
			order_id = r['order_id']
			detail = self.check_future_filled(order_id=order_id)
			return detail


	def margin_transaction(self, **kwargs):
		spot_api = self._spot_api
		order_args = kwargs['order_args']
		vprint('\nplace margin order')
		r = spot_api.place_order(**order_args).json()

		time.sleep(0.2)

		if bool(r['result']):
			order_id = r['order_id']
			detail = self.check_margin_filled(order_id=order_id)
			return detail
		else:
			vprint('place margin order fail')
			return self.margin_transaction(**kwargs)

	

	#input future size future size spot price
	def open(self, **kwargs):
		future_fiat_amount = int(kwargs['future_fiat_amount'])
		future_price = float(kwargs['target']['future_price'])
		spot_price = float(kwargs['target']['spot_price'])

		future_order_args = {
			'side': 'open',
			'fiat_amount': future_fiat_amount,
		}


		margin_order_args = dict()

		if future_price > spot_price:
			future_order_args['option'] = 'short'
			
			future_detail = self.future_transaction(order_args=future_order_args)

			#return true
			if future_detail:
				crypt_amount = float(future_detail['crypt_amount'])
				#use last_price to approximate amount
				margin_fiat_amount = spot_price*crypt_amount
				
				margin_order_args['side'] = 'buy'
				margin_order_args['fiat_amount'] = str(margin_fiat_amount)
				margin_detail = self.margin_transaction(order_args=margin_order_args)

				future_detail['option'] = 'short'
				margin_detail['option'] = 'long'

				#return detail
				return {'future': future_detail, 'margin': margin_detail}
				

		elif spot_price > future_price:
			future_order_args['option'] = 'long'

			future_detail = self.future_transaction(order_args=future_order_args)

			if future_detail:
				margin_order_args['side'] = 'sell'
				margin_order_args['crypt_amount'] = future_detail['crypt_amount']
				margin_detail = self.margin_transaction(order_args=margin_order_args)
				
				future_detail['option'] = 'long'
				margin_detail['option'] = 'short'

				#return detail
				return {'future': future_detail, 'margin': margin_detail}

		#fail
		return False


		#input future_detail, margin_detail
	def close(self, **kwargs):
		selected_position = kwargs['position']
		future_position_detail = selected_position.future
		margin_position_detail = selected_position.margin



		spot_price = float(kwargs['target']['spot_price'])

		future_order_args = {
			'side': 'close',
			'fiat_amount': future_position_detail['fiat_amount'],
		}

		if future_position_detail['option'] == 'long':

			future_order_args['option'] = 'long'
			future_transaction_detail = self.future_transaction(order_args=future_order_args)

			if future_transaction_detail:
				margin_order_args = {
					'side': 'buy',
					'fiat_amount': float(margin_position_detail['fiat_amount']),
				}
				margin_transaction_detail = self.margin_transaction(order_args=margin_order_args)
				return {'future': future_transaction_detail, 'margin': margin_transaction_detail}

		elif future_position_detail['option'] == 'short':
			future_order_args['option'] = 'short'
			future_transaction_detail = self.future_transaction(order_args=future_order_args)

			if future_transaction_detail:
				margin_position_fiat_amount = float(margin_position_detail['fiat_amount'])
				target_margin_crypt_amount = margin_position_fiat_amount / spot_price

				margin_order_args = {
					'side': 'sell',
					'crypt_amount': target_margin_crypt_amount,
				}

				
				margin_transaction_detail = self.margin_transaction(order_args=margin_order_args)
				vprint('repay loan')
				available_fiat = self._spot_api.get_margin_account().json()['currency:USDT']['available']
				r = self._spot_api.repay_loan('usdt', available_fiat)
				vprint(r.json())
				return {'future': future_transaction_detail, 'margin': margin_transaction_detail}


		#fail
		return False


	def safe(self):
		future_r = self._future_api.get_account().json()
		future_avail_balance = float(future_r['total_avail_balance'])


		margin_target_key = 'currency:{}'.format(self._spot_api._API_config['currency'])
		margin_r = self._spot_api.get_margin_account().json()

		if margin_r['risk_rate'] == '':
			spot_margin_risk_rate = 999
		else:
			spot_margin_risk_rate = float(margin_r['risk_rate'])


		future_threshold = float(self._manager_config['future_balance_threshold'])
		margin_threshold = float(self._manager_config['margin_risk_threshold'])


		vprint('(position_manager)future available balance:', future_avail_balance)
		vprint('(position_manager)margin risk rate:', spot_margin_risk_rate)
			
		if future_avail_balance >= future_threshold and spot_margin_risk_rate >= margin_threshold:
			vprint('(position_manager)safe')
			return True
		else:
			vprint('(position_manager)not safe')
			return False