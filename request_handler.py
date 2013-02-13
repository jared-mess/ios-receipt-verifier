import os
import sys
#import redis
import json
import logging

from tornado.web import RequestHandler, asynchronous
from tornado import httpclient

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
#redis = redis.from_url(redis_url)

log = logging.getLogger('tornado.general')

class MainHandler(RequestHandler):
    @asynchronous
    def post(self, game_name):
        """
        Get the json data and send it to apple to be verified
        """
        log.info(game_name)
        content = json.loads(self.request.body)
        header  = {'Content-Type' : 'application/json'}
        request = httpclient.HTTPRequest('https://sandbox.itunes.apple.com/verifyReceipt',
                                         method='POST',
                                         headers=header,
                                         body=json.dumps(content))
        
        http_client = httpclient.AsyncHTTPClient()
        http_client.fetch(request, self._validate_response)
    
    def _validate_response(self, response):
        """
        The callback from request hander when data is received
        
        Reads the json data returned, stores the transaction id so it can't be used again
        """
        receipt_data = json.loads(response.body)
        validation = dict()
        log.info(response.body)
        validation['valid_receipt'] = True
        if receipt_data['status'] != 0:
            self.set_status(403)
            validation['valid_receipt'] = False
            
        self.write(json.dumps(validation))
        self.finish()
        
    def get(self, game_name):
        logging.info('Get game Name %s' %game_name)
        self.write('here')
        
        
        

