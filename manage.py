from code.apps.trade.hedge import action as trade_action
from code.apps.datamining.hedge import action as mine_action
import os
from argparse import ArgumentParser


def main():
	argparse = ArgumentParser()
	parser1 = argparse.add_argument('action')
	ROOT_DIR = os.path.dirname((os.path.abspath(__file__)))
	
	args = argparse.parse_args()
	if args.action == 'trade':
		trade_action.start_trading(ROOT_DIR)
	elif args.action == 'mine':
		mine_action.start_mining(ROOT_DIR)

if __name__ == '__main__':
	main()