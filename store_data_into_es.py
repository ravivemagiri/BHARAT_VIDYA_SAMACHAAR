#import necessary modules
import csv
import pdb
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import os
import csv
import hashlib
import glob

def get_csv_data():

    data_records = []
    #pdb.set_trace()
    course_files = glob.glob('courses_data/*.csv')
    for each_course in course_files:
        reader = csv.DictReader(open(each_course))
        for raw in reader:
            try:
                record_info = dict(raw)
                modify_dic = {}
                modify_dic['title'] = record_info['title']
                if 'provider' in record_info:
                    modify_dic['provider'] = record_info['provider']
                if '\ufeffprovider' in record_info:
                    modify_dic['provider'] = record_info['\ufeffprovider']
                modify_dic['desc'] = record_info['desc']
                modify_dic['language'] = record_info['language']
                modify_dic['thumbnail'] = record_info['thumbnail']
                modify_dic['url'] = record_info['url']
                modify_dic['price'] = record_info['price']
                modify_dic['rating_count'] = record_info['rating_count']
                data_records.append(modify_dic)
            except:
                
                continue
   
    return data_records

def create_index(es_object, index_name = 'my_athina'):
    created = False
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            status = es_object.indices.create(index=index_name,ignore=400)
        created = True
    except Exception as e:
        print ("Exception occured in create_index: ", str(e))
    finally:
        return (created)

def es_search(es_object, index_name, search_string, args_hash={}):
    #search_object = {'query': {'match': {'name': {'query':search_string,"operator": "and","fuzziness": "AUTO"}}}}
        #args_hash['filter_word'] = 'data_camp'
        query_res = []
        args_hash['language'] = 'English'
        if 'filter_word' in args_hash and not 'concat_word' in args_hash:
            #search_object = {'query': {'match': {'name': {'query':search_string,"operator": "and","fuzziness": "AUTO"}}},"bool":{"filter":{"term": {"provider": "udemy"}}}}
            query_res = []
            for fil_word in args_hash['filter_word']:
                search_object = {'size' : 3000,
                                'query': {
                                    'bool':{
                                        'must':{'multi_match': {"query": search_string,"operator": "and","fuzziness": "AUTO", "fields": ['title']}},
                                        'filter':{"term":{"provider":fil_word}}
                                            }
                                        }
                                }
                json_obj = json.dumps(search_object)
                query_output_dic = es_object.search(index=index_name, body=json_obj)
                for res_record in query_output_dic['hits']['hits']:
                    record_dic = res_record['_source']
                    record_dic['_id']= res_record['_id']
                    query_res.append(record_dic)
        else:
            if 'concat_word' in args_hash or " " in args_hash:
                search_object = {'size' : 3000,'query': {'bool':{'must':{'multi_match': {"query": search_string,"operator": "and", "fields": ['title']}},'filter':{"term":{"language":'english'}}}}}
            else:
                search_object = {'size' : 3000,'query': {'bool':{'must':{'multi_match': {"query": search_string,"operator": "and","fuzziness": "AUTO", "fields": ['title']}},'filter':{"term":{"language":'english'}}}}}
            json_obj = json.dumps(search_object)
            query_output_dic = es_object.search(index=index_name, body=json_obj)
            query_res = []
            for res_record in query_output_dic['hits']['hits']:
                record_dic = res_record['_source']
                record_dic['_id']= res_record['_id']
                query_res.append(record_dic)
        return query_res

# def es_search(es_object, index_name, search_string):
#     query_res = []
#     search_object = {'query': {'match': {'COMPANY NAME': {'query':search_string,"operator": "and"}}}}
#     json_obj = json.dumps(search_object)
#     query_output_dic = es_object.search(index=index_name, body=json_obj)
#     for res_record in query_output_dic['hits']['hits']:
#         record_dic = res_record['_source']
#         record_dic['_id']= res_record['_id']
#         query_res.append(record_dic)
#     return query_res

def bulk_indexing(es_object, index_name, doc_type, records):
    """
    Bulk Indexing the documents.
    """
    documents_list = []
    try:
        for record in records:
            try:
                hash_id = hashlib.md5(record['url'].encode('utf')).hexdigest()
            except:
                continue
            document = {
                "_index": index_name,
                "_type": doc_type,
                "_id": hash_id,
                "_source": record
                }
            documents_list.append(document)
        status = helpers.bulk(es_object, documents_list, chunk_size=10)
        if (status[0] != len(records)):
            print("Error in bulk_indexing.")
    except Exception as e:
        print ('Exception occured in bulk_indexing: ', str(e))

def get_company_info(es_object, index_name, cin):
    reg_sta = {'registration_status':False}
    if es_object.exists(index=index_name,id=cin):
        company_details = es_object.get(index=index_name,id=cin)
        reg_sta['registration_status'] = True
        reg_sta.update(company_details['_source'])
    return reg_sta



# #slist_of_records = get_csv_data()

# es_object = Elasticsearch([{'host': 'localhost', 'port': 9200}])
# #pdb.set_trace()
# args_hash = {}
# # args_hash['filter_word']= ['udemy']
# res  = es_search(es_object, 'solveforbharat_v1', 'python',args_hash)
# if es_object.ping():
#     try:
#         status = create_index(es_object, 'solveforbharat_v1')
#         if (status):
#             store_data_in_es = bulk_indexing(es_object, 'solveforbharat_v1', 'providers_data', list_of_records)
#             #store_data_in_es = store_record(es_object, 'athina', list_of_records)
#         else:
#             print("Error in index creation.")
#     except Exception as e:
#         print('Exception in driver program: ', str(e))
# else:
#     print('ES object is down')

# pdb.set_trace()
# print('debug point')