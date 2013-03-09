import os
import sys
import redis
import json
import logging

from tornado.web import RequestHandler, asynchronous
from tornado import httpclient, gen

redis_url  = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_pool = redis.from_url(redis_url)

log = logging.getLogger('tornado.general')

class MainHandler(RequestHandler):
    @asynchronous
    @gen.engine
    def post(self, game_name):
        """
        Get the json data and send it to apple to be verified
        """       
        content = json.loads(self.request.body)
        
        header  = {'Content-Type' : 'application/json'}
        request = httpclient.HTTPRequest('https://sandbox.itunes.apple.com/verifyReceipt',
                                         method='POST',
                                         headers=header,
                                         body=json.dumps(content))
        
        
        
        http_client = httpclient.AsyncHTTPClient()
        #http_client.fetch(request, self._validate_response)
        response = yield gen.Task(http_client.fetch(request))
        
        receipt_data = json.loads(response.body)
        
        if receipt_data['status'] != 0:
            self.set_status(403)
            
        else:
            # try to add the receipt to the DB
            if redis_pool.sadd(receipt_data['bid'], receipt_data['transaction_id']) :
                redis_pool.zincrby(game_name, receipt_data['product_id'], 1)
                self.set_status(200)
            else:
                self.set_status(403)
        
        self.finish()
        
    def get(self, game_name):
        """
        Display Analytics for a specific game
        """
        logging.info('Get game Name %s' %game_name)
        
        self.write(json.dumps(redis_pool.zrange(game_name, 0, 20, desc=True, withscores=True)))
        
        
        

