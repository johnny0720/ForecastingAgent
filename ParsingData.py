#!/usr/bin/env python
# coding: utf-8

# In[129]:


import os
import json
import csv
import time
from datetime import date
import requests
import pandas as pd 


# In[130]:


class CrawlerController(object):
    '''Split targets into several Crawler, avoid request url too long'''

    def __init__(self, targets, max_stock_per_crawler=50):
        self.crawlers = []

        for index in range(0, len(targets), max_stock_per_crawler):
            crawler = Crawler(targets[index:index + max_stock_per_crawler])
            self.crawlers.append(crawler)

    def run(self):
        data = []
        for crawler in self.crawlers:
            data.extend(crawler.get_data())
        return data

class Crawler(object):
    '''Request to Market Information System'''
    def __init__(self, targets):
        endpoint = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp'
        # Add 1000 seconds for prevent time inaccuracy
        timestamp = int(time.time() * 1000 + 1000000)
        channels = '|'.join('tse_{}.tw'.format(target) for target in targets)
        print(channels)
        self.query_url = '{}?_={}&ex_ch={}'.format(endpoint, timestamp, channels)

    def get_data(self):
        try:
            # Get original page to get session
            req = requests.session()
            req.get('http://mis.twse.com.tw/stock/index.jsp',
                    headers={'Accept-Language': 'zh-TW'})

            response = req.get(self.query_url)
            content = json.loads(response.text)
        except Exception as err:
            print(err)
            data = []
        else:
            data = content['msgArray']

        return data

class Recorder(object):
    '''Record data to csv'''
    def __init__(self, path =r"C:\Users\aren9\OneDrive\桌面\jupyter_workplace\stock_data"):
        self.folder_path = '{}/{}'.format(path, date.today().strftime('%Y%m%d'))
        if not os.path.isdir(self.folder_path):
            os.mkdir(self.folder_path)

    def record_to_csv(self, data):
        for row in data:
            try:
                file_path = '{}/{}.csv'.format(self.folder_path, row['c'])
                with open(file_path, 'a') as output_file:
                    writer = csv.writer(output_file, delimiter=',')
                    writer.writerow([
                        row['c'],
                        row['t'],# 資料時間
                        row['z'],# 最近成交價
                        row['tv'],# 當盤成交量
                        row['v'],# 當日累計成交量
                        #row['a'],# 最佳五檔賣出價格
                        #row['f'],# 最價五檔賣出數量
                        #row['b'],# 最佳五檔買入價格
                        #row['g']# 最佳五檔買入數量
                    ])

            except Exception as err:
                print(err)


# In[131]:


targets = [_.strip() for _ in open(r"C:\Users\aren9\OneDrive\桌面\jupyter_workplace\stock_number.cvs", 'r')]


# In[132]:


controller = CrawlerController(targets)


# In[133]:


data = controller.run()


# In[134]:


recorder = Recorder()


# In[135]:


recorder.record_to_csv(data)


# In[136]:


tsmc = pd.read_csv(r"C:\Users\aren9\OneDrive\桌面\jupyter_workplace\stock_data\20230620\2330.csv",header=None)
tsmc.columns = ['stock_number','Time', 'latest_deal', 'current_volume', 'Cumulative_volume']


# In[137]:


tsmc


# In[ ]:




