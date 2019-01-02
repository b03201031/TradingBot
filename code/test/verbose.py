import configparser
import os


root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
setting_path = os.path.join(root_path, 'config/setting.conf')
config_parser = configparser.ConfigParser()
config_parser.read(setting_path)

if config_parser['TEST']['verbose'] == 'yes':
	print('verbose on')
	def vprint(*args):
		for arg in args:
			if arg == 'split line':
				print('------------------------------------------------------', end='')
				break
			print(arg, end='')
		print()
elif config_parser['TEST']['verbose'] == 'no':
	print('verbose off')
	vprint = lambda *args: None