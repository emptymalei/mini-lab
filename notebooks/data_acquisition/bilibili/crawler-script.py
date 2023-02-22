import numpy as np
import os
from time import sleep

from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
# import pathos.multiprocessing as mp

import json
import requests

import datetime

api_url_base = 'https://api.bilibili.com/x/article/archives?ids='
fields_stat = ['aid', 'view', 'danmaku', 'reply', 'favorite', 'coin', 'share', 'now_rank', 'his_rank', 'like']
vid_data_file = 'vid_data.csv'
failed_vid = 'failed_vid_data.csv'
prs = 3 # define the number of processes
retry_lvl = [100, 0.1]

# set request to cloose tcp connections automatically
# requests.session(config = { 'keep_alive': False })

beg = 1
end = 10000
#end = 23000000
seg = 100
flag = beg
flag_falied = 0
batch_size = 5

print('job started at: '+ str(datetime.datetime.now()) + '\n' )
print('start from: '+str(beg) +'; end at: ' +str(end) + '\n' )



def modeit(filename, fields = None):

    if fields == None:
        fields = ['aid', 'view', 'danmaku', 'reply', 'favorite', 'coin', 'share', 'now_rank', 'his_rank', 'like']

    if os.path.exists(filename):
        mode_write = 'a' # append if already exists
    else:
        mode_write = 'w' # make a new file if not
        with open(filename, mode_write) as f:
            f.write( ','.join(fields) + '\n' )
        print(filename + ' created!' + '\n' + 'Fields are '+ ','.join(fields) + '\n')

    return mode_write


def crawler(vids):

    # print(vids)
    # return [  ]
    try_flag = 0

    while True and (try_flag < retry_lvl[0]):
        try:
            with requests.Session() as s:
                resp = s.get( api_url_base + ','.join(vids) )
        except requests.exceptions.RequestException as err:
            print('request error', err)
            try_flag = try_flag + 1
            sleep(try_flag * retry_lvl[1])
            pass
        else:
            break

    #except Exception as ex:
    #    print(str(ex))

    if resp.json()['code']==0:
        resp.json()['data']
        vid_list_return = list(resp.json()['data'].keys())
        vid_list_data = [ [ str(resp.json()['data'][ vid ]['stat'][fid]) for fid in fields_stat] for vid in vid_list_return]
        return [vid_data for vid_data in vid_list_data]
    else:
        print('Empty return from request')
        return []





def VidDumpSingle(data, fileobj):
    """
    Record a list of data
    """

    data_dump = (','.join(data) ) + '\n'
    fileobj.write( data_dump )


def VidDumpBatch(dataArr, fileobj):
    """
    Record a list of data
    """

    data_dump = '\n'.join( [(','.join(data) ) for data in dataArr] ) + '\n'

    fileobj.write( data_dump )




def VidBatcherSingle( vid_start, vid_end, vids_size ):
    """
    Batches ids within the range [vid_start, vid_end). Each list inside the batch contains vids_size vids.
    """

    bat_list_f = []

    for i in range(vid_start, vid_end - vids_size, vids_size ):

        bat_list_f = bat_list_f + [ list( range( i, i+ vids_size ) ) ]

    bat_list_f = bat_list_f + [ list( range( i+vids_size, vid_end ) ) ]

    return bat_list_f







modeit(vid_data_file, fields_stat)
data_mode = modeit(vid_data_file)

print('File mode is set to '+str(data_mode))

for i in range(beg, end, batch_size*seg):


    batch_start = i
    batch_end = i + seg * batch_size

    with open(vid_data_file, data_mode) as f:#Open data file

        # for vids_in_run in VidBatcherSingle( batch_start, batch_end, seg ):#loop through this segment of ids
        #     vids_in_run = [ str(i) for i in vids_in_run ]
        #     records = crawler(vids_in_run)
        #
        #     with ThreadPool(2) as p:
        #        records = p.map(crawler, [vids_in_run])
        #
        #     file_cache = file_cache +  records[0]

#         print(file_cache)

        with ThreadPool(prs) as p:
           records = p.map(crawler, [ [ str(i) for i in vids_in_run ] for vids_in_run in VidBatcherSingle( batch_start, batch_end, seg )] )



        # print('records length: ' + str( len(records) ) + '\n' )
        # print('each record length: ' + str( len(records[0]) ) + '\n' )
        # print('0 the element of the first record length: ' + str( len(records[0][0]) ) + '\n' )
        # print(records)
        records_flatten = [item for sublist in records for item in sublist]
        VidDumpBatch(records_flatten, f)




print('job finished at: '+ str(datetime.datetime.now()) + '\n' )
