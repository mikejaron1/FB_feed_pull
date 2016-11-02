import urllib2
import requests
import json
import pandas as pd 
import datetime
import os
import csv
import time

from config import *

def url_creator(auth, pageID, fields):
	'''
	Takes in arguments and returns the search url needed
	'''

	base_url =  "https://graph.facebook.com/v2.7/"
	access = "&access_token="+auth
	fields = "?fields="+fields
	main_url = base_url+pageID+fields+access

	return main_url


def graph_api(url):
	'''
	takes in complete URL, calls the api and returns the page
	'''

	test = urllib2.urlopen(url)
	page = json.loads(test.read())
	# data = page['data']
	return page



def feed_comment_search(url, field, store, ID):
	'''
	THis
	'''

	type_list = []
	text_list = []
	ID_list = []
	created_times = []
	store_list = []
	og_id = []
	like_count = []

	paginataion = True
	first = True
	page_count = 0
	while paginataion:
		try:
			main_output = graph_api(url)
			if first:
				output = main_output[field]['data']
			else:
				output = main_output['data']
		except:
			# print "nothing on this page"
			paginataion = False

		if paginataion:
			# print page_count, "page count"

			if first:
				try: 
					url = main_output[field]['paging']['next']
				except:
					paginataion = False
			else:
				# output = main_output['data']
				try:
					url = main_output['paging']['next']
				except:
					paginataion = False

			for i in output:
				try:
					text_list.append(i['message'])
				except:
					try:
						text_list.append(i['story'])
					except:
						continue
				type_list.append(field)
				store_list.append(store)
				ID_list.append(i['id'])
				created_times.append(i['created_time'])
				og_id.append(ID)

				if i['created_time'] < time_stop and field == 'feed':
					paginataion = False
					print "time stopped"
					break
		
		page_count += 1
		first = False

	return type_list, ID_list, store_list, text_list, created_times, og_id



def write_to_csv(field,type_list, ID_list, store_list, text_list, created_times, og_id):
	## after loop is done, assuming that is all for the page write it all to the csv
	if len(ID_list) > 0:
		new_df = pd.DataFrame()
		new_df['store'] = store_list
		new_df['type'] = type_list
		new_df['OG_feed_id'] = og_id
		new_df['ID'] = ID_list
		new_df['created_time'] = created_times
		new_df['text'] = text_list

		filename = os.getcwd()+'/results/'+store+'.csv'
		if not os.path.isfile(filename) or field == 'feed':
			new_df.to_csv(filename, encoding='utf-8', index=False)
		else: # else it exists so append without writing the header
			new_df.to_csv(filename, mode = 'a', header=False, encoding='utf-8', index=False)
	



def like_counter(url, field="likes"):
	'''
	comments
	'''


	paginataion = True
	first = True
	total = 0

	while paginataion:
		try:
			main_output = graph_api(url)
			if first:
				output = main_output[field]['data']
			else:
				output = main_output['data']
		except:
			# print "nothing on this page"
			paginataion = False

		if paginataion:
			if first:
				try: 
					url = main_output[field]['paging']['next']
				except:
					paginataion = False
			else:
				# output = main_output['data']
				try:
					url = main_output['paging']['next']
				except:
					paginataion = False


			total += len(output)
			
		first = False

	like_count = total

	return like_count



def main(store):
	
	field = 'feed'
	url = url_creator(auth, store, field)
	type_list, ID_list, store_list, text_list, created_times, og_id = \
						feed_comment_search(url, field, store, ID='na')

	write_to_csv(field, type_list, ID_list, store_list, text_list, \
					created_times, og_id)
	
	print '\n'
	print "done with feed"
	print "starting comment seach for %s ids" % len(ID_list)
	print '\n'
	
	if len(ID_list) <= 0:
		print "nothing in feed"
	else:
		feed_ids = ID_list

		new_dict = {}
		new_id_list = []
		like_count_list = []
		for count, ID in enumerate(feed_ids): 
			if round((count/float(len(feed_ids)))*100,0) % 5 == 0:
				print round((count/float(len(feed_ids)))*100,2), ' percent done'
			field = 'comments'
			url = url_creator(auth, ID, field)
			
			type_list, ID_list, store_list, text_list, created_times, og_id = \
			feed_comment_search(url, field, store, ID)

			### continue to search for children as deep as possible
			### AKA find comments of comments of comments .....
			feed_ids.extend(ID_list)


			field2 = "likes"
			url = url_creator(auth, ID, field2)
			like_count = like_counter(url)
			new_dict[ID] = like_count

			write_to_csv(field, type_list, ID_list, store_list, text_list, \
						created_times, og_id)

		og_df = pd.read_csv(os.getcwd()+'/results/'+store+'.csv')
		temp_like_list = [new_dict[i] for i in og_df['ID']]
		og_df['like_count'] = temp_like_list
		## change up the column order
		og_df = og_df[['store', 'type', 'OG_feed_id', 'ID', 'created_time', 'like_count','text']]
		og_df.to_csv(os.getcwd()+'/results/'+store+'.csv', index=False)



	

if __name__ == '__main__':
	
	## auth test
	# url = url_creator(auth, 'me', fields)
	# main_output = graph_api(url)

	## what files are you using
	if test:
		page_ids = [test_store]
		difference = page_ids
	else:
		if supercenter_file == False:
			## for new dataset with FB users
			df = pd.read_csv(file_name)
			page_ids = df['FacebookId']
			page_ids = page_ids.dropna()
			page_ids = [int(page) for page in page_ids]  #change it from float
		else:
			# for original dataset
			df = pd.read_csv(file_name)
			page_ids = df['fblink']
			page_ids = [page[page.find('com/')+4:] for page in page_ids]

		## find what has already been done
		difference = list(set(page_ids) - set(done_files) - set(does_not_exist))

	## add on most recent file to be done again, in case it stopped b4 it was 100% done
	## just needs to be uncommented if stops b4 100% done
	# difference.insert(0,max_file[:max_file.find('.csv')])

	store_count = 0
	for store in difference:
		start_time = time.time()
		# if 'Walmart' in store:
		if store > 0:
			print store
			main(str(store))

			total_time = time.time()-start_time
			print total_time, "took this long"
			# time.sleep(60)
		store_count += 1
		print store_count, "store index"
		



	