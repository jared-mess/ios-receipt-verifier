import os
#import redis
import json
import logging

from tornado.web import RequestHandler, asynchronous
from tornado import httpclient

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
#redis = redis.from_url(redis_url)

logging.basicConfig( 
    stream=sys.stdout, 
    level=logging.DEBUG, 
    format='"%(asctime)s %(levelname)8s %(name)s - %(message)s"', 
    datefmt='%H:%M:%S' 
) 

class MainHandler(RequestHandler):
    @asynchronous
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
        http_client.fetch(request, self._validate_response)
    
    def _validate_response(self, response):
        """
        The callback from request hander when data is received
        
        Reads the json data returned, stores the transaction id so it can't be used again
        """
        receipt_data = json.loads(response.body)
        validation = dict()
        logging.info(response.body)
        validation['valid_receipt'] = True
        if receipt_data['status'] != 0:
            validation['valid_receipt'] = False
            
        self.write(json.dumps(validation))
        self.finish()
        
        

