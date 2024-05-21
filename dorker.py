# Imports
import argparse
import requests
import random
from time import sleep
from datetime import datetime
from colorama import Fore, Style
from bs4 import BeautifulSoup

# Classes
class log:
	def get_time():
		return datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')

	def system(message):
		return print(Fore.YELLOW + '[~] ' + Fore.LIGHTBLACK_EX + log.get_time() + Style.RESET_ALL + str(message))

	def success(message):
		return print(Fore.GREEN + '[+] ' + Fore.LIGHTBLACK_EX + log.get_time() + Style.RESET_ALL + str(message))

	def error(message):
		return print(Fore.RED + '[!] ' + Fore.LIGHTBLACK_EX + log.get_time() + Style.RESET_ALL + str(message))

# Functions
def banner():
	print(Fore.YELLOW + r'''
         _         _           
      __| |___ _ _| |_____ _ _ 
     / _` / _ \ '_| / / -_) '_|
     \__,_\___/_| |_\_\___|_|  
    ''' + Fore.LIGHTBLACK_EX +
	''' v0.1   -   github.com/crsn
	''' + Style.RESET_ALL)

def arguments():
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawTextHelpFormatter,
		usage='%(prog)s -u [url] [options]'
	)
	parser.add_argument(
		'-u',
		metavar='[url]',
		help='url to target for dorks',
		type=str,
		required=True
	)
	parser.add_argument(
		'-t',
		metavar='[type]',
		help='type of dorks to identify (default: all)\ntypes: file, sqli, error, subdomain, document, all',
		type=str,
		default='all'
	)
	parser.add_argument(
		'-d',
		metavar='[interval]',
		help='duration to sleep between requests (default: random)',
		type=int,
		default=None
	)

	return parser.parse_args()

def get_dork(type, target):
	file_dorks = [
		# Exposed configuration files
		'ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini site:' + target,
		# Exposed log files
		'ext:log site:' + target,
		# Exposed backup files
		'ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup site:' + target,
		# Exposed database files
		'ext:sql | ext:dbf | ext:mdb site:' + target
	]

	sqli_dorks = [
		# Index page
		'allinurl:index.php?id= site:' + target,
		'allinurl:index.php?pid= site:' + target,
		'allinurl:index.php?page= site:' + target,

		# Product page
		'allinurl:product.php?id= site:' + target,
		'allinurl:product.php?pid= site:' + target,
		'allinurl:product.php?sku= site:' + target,

		# Category page
		'allinurl:category.php?id= site:' + target,
		'allinurl:product.php?cid= site:' + target,
		'allinurl:product.php?cat= site:' + target,

		# News page
		'allinurl:news.php?id= site:' + target,
		'allinurl:news.php?article= site:' + target
	]

	error_dorks = [
		'intext:sql syntax near | intext:syntax error has occurred | intext:incorrect syntax near | intext:unexpected end of SQL command | intext:Warning: mysql_connect() | intext:Warning: mysql_query() | intext:Warning: pg_connect() site:' + target
	]

	subdomain_dorks = [
		'site:*.' + target
	]

	document_dorks = [
		'ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv site:' + target
	]

	match type:
		case 'file':
			return file_dorks
		case 'sqli':
			return sqli_dorks
		case 'error':
			return error_dorks
		case 'subdomain':
			return subdomain_dorks
		case 'document':
			return document_dorks
		case 'all':
			return file_dorks + sqli_dorks + error_dorks + subdomain_dorks + document_dorks

def send_request(dork):
	user_agents = [
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.18362 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
	]

	headers = {
		'User-Agent': random.choice(user_agents),
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.5'
	}

	url = 'https://google.com/search?q=' + dork
	response = requests.get(url, headers=headers)

	if response.status_code == 200:
		return response.text
	else:
		log.error('Failed to fetch response: HTTP Code ' + str(response.status_code))
		return None

def parse_results(html):
	soup = BeautifulSoup(html, 'html.parser')
	dorks = []
	
	for div in soup.find_all('div', class_='g'):
		a = div.find('a', href=True)

		if a and 'href' in a.attrs:
			dorks.append(a['href'])

	return dorks

def main():
	banner()
	
	argument = arguments()
	target = argument.u
	type = argument.t
	duration = argument.d

	dorks = get_dork(type, target)

	for dork in dorks:
		log.system('Searching for \'' + dork + '\'')
		
		query = send_request(dork)

		if query:
			results = parse_results(query)

			if results:
				for result in results:
					log.success('Link found: ' + result)
			else:
				log.error('Unable to find any links for \'' + dork + '\'')
		
		if duration:
			sleep(duration)
		else:
			sleep(random.uniform(3, 20))

if __name__ == '__main__':
	main()
