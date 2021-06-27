from flask import request,jsonify,Response
from flask_restx import Namespace, Resource, fields
from http import HTTPStatus
from app.tasks import *
from connection import SQLDB
from datetime import datetime, timedelta

namespace = Namespace('MFTS','resource endpoints', '/v1/trading-system')


resources_model=namespace.model('Resources',{
    'access_key': fields.String(
        required=True,
        description='AWS access key'
    ),
    'secret_key': fields.String(
        required=True,
        description='AWS secret key'
    ),
    'seriaized':fields.Boolean()
})


@namespace.route('/sectors')
class sectors(Resource):
    @namespace.response(200, 'Success')
    @namespace.response(500, 'Internal Server error')
    def get(self):
        '''Get list of all the sectors'''
        self.__dbconn=SQLDB()
        result=self.__dbconn.execute_query('select distinct "Sector" from "stockmaster"')
        return jsonify(result)

@namespace.route('/stocks')
class stocks(Resource):
    @namespace.response(200, 'Success')
    @namespace.response(500, 'Internal Server error')
    def get(self):
        '''Get list of all the stocks'''
        self.__dbconn=SQLDB()
        result=self.__dbconn.execute_query('SELECT "Id", "Symbol", "Name", "Volume", "Sector", "Industry" FROM "stockmaster"')
        return jsonify(result)

@namespace.route('/stocks/<string:stock_name>')
class stock(Resource):
    @namespace.response(200, 'Success')
    @namespace.response(500, 'Internal Server error')
    def get(self,stock_name):
        '''Get stock info'''
        self.__dbconn=SQLDB()
        result=self.__dbconn.get_tickr(stock_name)
        if result.empty:
            return jsonify("Not found")
        return Response(result.to_json(orient='records'),mimetype='application/json')




@namespace.route('/stocks/details/<string:stock_name>')
class stockdetails(Resource):
    @namespace.response(200, 'Success')
    @namespace.response(500, 'Internal Server error')
    def get(self,stock_name):
        '''Get stock info'''
        self.__dbconn=SQLDB()
        stock_info=self.__dbconn.get_tickr(stock_name)
        if stock_info.empty:
            return jsonify("Not found")
        result=self.__dbconn.get_stock_details(stock_info.iloc[0]["Id"],datetime.now().strftime("%Y-%m-%d"),datetime(2012,5,12).strftime("%Y-%m-%d"))
        if result.empty:
            return jsonify("Not found")
        return Response(result.to_json(orient='records'),mimetype='application/json')
        

# @namespace.route('/resources')
# class awsresources(Resource):
#     '''Get data for all the resources'''
#     @namespace.response(202, 'Accepted')
#     @namespace.response(500, 'Internal Server error')
#     def get(self):
#         '''Get all the AWS resources'''
#         task = None
#         return {"IsSuccess": True,"Message":"The task has been accepted on the queue\n","Data":task.id}, 202

# @namespace.route('/<string:service_name>')
# class awsresource(Resource):
#     '''Get specific AWS Resource'''
#     @namespace.response(404, 'Resource not found')
#     @namespace.response(500, 'Internal Server error')
#     def get(self, service_name):
#         '''Get specific AWS resource'''
#         try:
#             task = get_service_info.delay(service_name)
#             return {"IsSuccess": True,"Message":"The task has been accepted on the queue\n","Data":task.id}, 202
#         except Exception as e:
#             return {"IsSuccess": False,"Message":str(e),"Data":None}, 404

# @namespace.route('/services')
# class awsservices(Resource):
#     @namespace.response(200, 'Success')
#     @namespace.response(500, 'Internal Server error')
#     def get(self):
#         '''Get all the services supported by the acclerator'''
#         try:
#             a=AWSAcclerator()
#             result=a.get_all_services(Config.INPUT_FILE_LOCATION)
#             return {"IsSuccess": True,"Message":f"Total services count {len(result)}","Data":result}, 200
#         except Exception as e:
#             return {"IsSuccess": False,"Message":str(e),"Data":None}, 500

# @namespace.route('/status/<task_id>')
# class awstaskstatus(Resource):
#     @namespace.response(200, 'Success')
#     def get(self,task_id):
#         '''Get the current status of the task'''
#         task = long_task.AsyncResult(task_id)
#         if task.state == 'PENDING':
#             # job did not start yet
#             response = {
#                 'state': task.state,
#                 'status': 'In progress...'
#             }
#         elif task.state != 'FAILURE':
#             response = {
#                 'state': task.state,
#                 'status': task.info.get('status', '')
#             }
#             if 'result' in task.info:
#                 response['result'] = task.info['result']
#         else:
#             # something went wrong in the background job
#             response = {
#                 'state': task.state,
#                 'status': str(task.info),  # this is the exception raised
#             }
#         return jsonify(response)

    
