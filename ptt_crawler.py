import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup

from conn_info import connect_db

PTT_URL = 'https://www.ptt.cc'
BOARD = ['NSwitch']
start_date = '20200406'
end_date = '20200406'

def get_web_page(url):
	try:
		res = requests.get(url)
		# sucessful response
		if res.status_code == 200:
			return res.text
		# failed response
		else:
			print('Wrong status code:', res.status_code)
			return None
	except TypeError:
		print('Cannot get webpage.')
		return None


def get_articles(dom, start_date, end_date, conn):
	soup = BeautifulSoup(dom, 'lxml')
	paging_div = soup.find('div', 'btn-group btn-group-paging')
	prev_url = paging_div.find_all('a')[1]['href']

	articles = []
	divs = soup.find_all('div', 'r-ent')
	start_date = datetime.strptime(start_date, '%Y%m%d')
	end_date = datetime.strptime(end_date, '%Y%m%d')
	for d in divs:
		current_year = datetime.now().strftime('%Y')
		article_time = current_year + '/' + d.find('div', 'date').text.strip()
		article_time = datetime.strptime(article_time, '%Y/%m/%d')
		if article_time >= start_date and article_time <= end_date:
			if d.find('a'):
				href = PTT_URL + d.find('a')['href']
				try:
					article = get_content(href)
				except TypeError:
					print('Wrong format on this page:', href)
					continue
				save_article(article, conn)
				save_push(article['push'], conn)
				articles.append(article)
	return articles, prev_url
	

# Get all the content on one article page
## authorId, authorName, category, title, publishedTime, content, canonicalUrl, 
## createdTime, commentId, commentContent, commentTime
def get_content(url):
	res = requests.get(url)
	soup = BeautifulSoup(res.text, 'lxml')

	# get article content
	span = soup.find_all('span', 'article-meta-value')
	author_id = span[0].text.strip().split('(')[0]
	author_name = span[0].text.strip().split('(')[1].replace(')', '')
	
	# print(span[2].text)
	title = span[2].text.strip()
	
	# time, datetime
	time = span[3].text.strip()
	dt = datetime.strptime(time, '%a %b %d %H:%M:%S %Y')

	# content
	end_at = u'--'
	main_content = soup.find(id='main-content').text.strip()
	content = main_content.split(time)[1].split(end_at)[0]

	# push (author, content, time)
	pushes = soup.find_all('div', 'push')
	push_list = []
	current_year = datetime.now().strftime('%Y')
	for push in pushes:
		push_author = push.find('span', 'f3 hl push-userid').text
		push_content = push.find('span', 'f3 push-content').text.lstrip(': ')
		if push.find('span', 'push-ipdatetime').text.strip():
			push_time = current_year + '/' + push.find('span', 'push-ipdatetime').text.strip()
			push_time = datetime.strptime(push_time, '%Y/%m/%d %H:%M')
		else:
			print('Time', push.find('span', 'push-ipdatetime').text.strip())
			push_time = None
		push_list.append({
			'push_author': push_author,
			'push_content': push_content,
			'push_time': push_time
		})
	article = {
		'title': title,
		'author_id': author_id,
		'author_name': author_name,
		# 'category': category,
		'time': dt,
		'content': content, 
		'url': url,
		'push': push_list
	}
	return article

def save_article(article, conn):
	cur = conn.cursor()
	cur.execute('''INSERT INTO article (
		title,
		author_id,
		author_name,
		time,
		content,
		url) VALUES (%s, %s, %s, %s, %s, %s)
		ON CONFLICT (article_id) DO NOTHING
			
		''', (
		article['title'],
		article['author_id'],
		article['author_name'],
		article['time'],
		article['content'],
		article['url'])
	)
	conn.commit()

def save_push(pushes, conn):
	cur = conn.cursor()
	cur.execute('SELECT article_id FROM article \
				ORDER BY article_id DESC LIMIT 1')
	article_id = cur.fetchall()[0][0]

	for p in pushes:
		cur.execute('''INSERT INTO push (
			push_author, 
			push_content,
			push_time,
			article_id) VALUES (%s, %s, %s, %s)''', (
			p['push_author'],
			p['push_content'],
			p['push_time'],
			article_id)
		)
		conn.commit()


def main():
	# 先用今天
	# today = datetime.now().strftime('%m/%d').lstrip('0')
	conn = connect_db()
	# conn = None
	for b in BOARD:
		url = '{}/bbs/{}/index.html'.format(PTT_URL, b)
		current_page = get_web_page(url)
		if current_page:
			current_articles, prev_url = get_articles(current_page, start_date, end_date, conn)
			while current_articles:
				current_page = get_web_page(PTT_URL+prev_url)
				current_articles, prev_url = get_articles(current_page, start_date, end_date, conn)
	conn.close()

if __name__ == "__main__":
	main()
	