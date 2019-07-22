# -*- coding:utf-8 -*-
import json
import typing
# from yct_task import my_customer,my_product
# from yct_task_two import my_product
from handle_data import tasks
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol
import pickle
import time
from handle_data.main import handle_data

##############################
from handle_data.tasks import handel_parameter, filter_step
import random

import recorder
logger=recorder.get_log().config_log('./logs/request.log')

import redis
from handle_data.celery_config import *
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
r = redis.Redis(connection_pool=redis_pool)

from handle_data.save_to_mysql import Save_to_sql
##############################

filter_info={'http_connect':['sh.gov.cn']}
class classification_deal:
    '''定义一个基类通过配置处理消息'''
    def filter_deal(self,flow):
        pass
    def other_dealdatabag(self,flow):
        pass
    def yct_dealdatabag(self,flow):
        pass
    def run_celery(self,data):
        pass


class Proxy(classification_deal):
    # HTTP lifecycle
    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        """
            An HTTP CONNECT request was received. Setting a non 2xx response on
            the flow will return the response to the client abort the
            connection. CONNECT requests and responses do not generate the usual
            HTTP handler events. CONNECT requests are only valid in regular and
            upstream proxy modes.
        """
    def requestheaders(self, flow: mitmproxy.http.HTTPFlow):
        """
            HTTP request headers were successfully read. At this point, the body
            is empty.
        """
        '''读取请求头内容'''

    def request(self, flow: mitmproxy.http.HTTPFlow):
        """
            The full HTTP request has been read.
        """
        # request_header=eval(dict(flow.request.headers)['request_header'])
        '''获取请求详细信息'''
        ####################################
        request = flow.request
        to_server = flow.request.url
        ###########start analysis###########
        '''1.排除无用的url请求'''
        if not request:
            return
        if not to_server:
            return
        if 'yct.sh' not in flow.request.url:
            return
        # 过滤 js,css,png,gif,jpg 的数据
        for end_name in ['.js', '.css', '.png', '.jpg', '.gif', '.ico']:
            if end_name in to_server:
                return

        '''2.初始数据，非urlencode或json格式的数据则置空'''
        parameters_dict = {}
        try:
            request_form = request.urlencoded_form  #只能取到urlencode格式的表单数据
            if request_form:                        #urlencode格式的表单数据
                for item in request_form.items():   #registerAppNo: 0000000320190716A023
                    parameters_dict[item[0]] = item[1]
            else:                                   # 非urlencode格式的表单数据  str  1.urlencode   2.json
                json_data = request.text
                parameters_dict = json.loads(json_data)
        except Exception as e:
            parameters_dict = {}
        if not parameters_dict:
            return

        # 1.非yct的请求 2.非css，js，jpg。。  3.非urlencode或json格式的，或空数据   4.过滤无用请求 -->不过滤了 都留着
        '''得到全数据parameters_dict'''

        flow.request.product_id = str(random.random())
        # '''区分不同页面的form 1.page_name=''错误的url 2.page_name=form_name 正确的url'''
        page_name = filter_step(to_server)

        # '''错误的url：parameters={无数据}      正确的url：parameters={有数据}'''
        # parameters = handel_parameter(parameters_dict, to_server)

        # analysis_data = {
        #     'product_id': flow.request.product_id,
        #     'customer_id': '',
        #     'methods': request.method,
        #     'web_name': request.host,
        #     'to_server': to_server,
        #     'time_circle': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        #     'parameters': parameters,
        #     'pageName': page_name,
        #     'anync': '',
        #     'isSynchronous': '0',
        #     'delete_set': False
        # }

        analysis_data_bak = {
            'product_id': flow.request.product_id,
            'customer_id': '',
            'methods': request.method,
            'web_name': request.host,
            'to_server': to_server,
            'time_circle': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            'parameters': json.dumps(parameters_dict),
            'pageName': page_name,
            'anync': '',
            'isSynchronous': '0',
            'delete_set': False
        }

        '''to_server,pagename,parameters,parameters_dict
        analysis_data    analysis_data_bak'''

        logger.info('product_id=%s to_server=%s pageName=%s ' % (flow.request.product_id,to_server,page_name))
        logger.info('product_id=%s parameters=%s ' % (flow.request.product_id, parameters_dict))
        logger.info('product_id=%s analysis_data_bak=%s' % (flow.request.product_id,analysis_data_bak))

        # if page_name:
        #     logger.info('start analysis_data_bak=%s' % analysis_data_bak)
        #     # apply_form的保存，会产生公司名称和yctAppNo
        #     if 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info' in to_server:
        #         logger.info('start apply_form-save:product_id=%s' % (flow.request.product_id))
        #         registerAppNo = parameters_dict.get('registerAppNo', '')
        #         yctAppNo = parameters_dict.get("yctAppNo", '') or parameters_dict.get('yctSocialUnit.yctAppNo', '')
        #         etpsName = parameters_dict.get('etpsApp.etpsName', '')
        #         # 将registerAppNo对应公司名称和yctAppNo对应公司名称，暂存到redis
        #         r.mset({registerAppNo: etpsName, yctAppNo: etpsName})
        #         analysis_data_bak['registerAppNo'] = registerAppNo
        #         analysis_data_bak['yctAppNo'] = yctAppNo
        #         analysis_data_bak['etpsName'] = etpsName
        #         analysis_data_bak['to_server'] = 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info'
        #         logger.info(
        #             'end apply_form:product_id=%s analysis_data_bak=%s ' % (name, analysis_data_bak))
        #         logger.info(
        #             'end apply_form:product_id=%s parameters=%s ' % (name, json.loads(parameters)))
        #
        #
        #     # 针对股东或成员的保存
        #     elif to_server in ['http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/save',
        #                        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_save_member']:
        #         logger.info('start investor-save&member-save:product_id=%s' % (name))
        #         registerAppNo = parameters_dict.get('appNo') or parameters_dict.get(
        #             'etpsMember.appNo')  # 注册公司对应的唯一的appNo
        #         # gdNo = response.text  # 股东对应的编号
        #         # analysis_data_bak['customer_id'] = gdNo
        #         analysis_data_bak['customer_id'] = ''
        #         analysis_data_bak['registerAppNo'] = registerAppNo
        #         if r.get(registerAppNo):
        #             analysis_data_bak['etpsName'] = r.get(registerAppNo).decode(encoding='utf-8') if isinstance(
        #                 r.get(registerAppNo), bytes) else r.get(registerAppNo)
        #             analysis_data_bak['yctAppNo'] = ''  # 股东没有yctAppNo，置为空
        #         logger.info(
        #             'end investor-save&member-save:product_id=%s analysis_data_bak=%s ' % (name, analysis_data_bak))
        #         logger.info(
        #             'end investor-save&member-save:product_id=%s parameters=%s ' % (name, json.loads(parameters)))
        #
        #     # 针对股东的删除
        #     elif 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/delete' in to_server:
        #         from urllib import parse
        #
        #         logger.info('start investor-delete:product_id=%s' % (name))
        #         params = parse.parse_qs(parse.urlparse(to_server).query)
        #         gdNo = params.get('id', [])[0]
        #         registerAppNo = params.get('appNo', [])[0]
        #         analysis_data_bak['customer_id'] = gdNo
        #         analysis_data_bak['registerAppNo'] = registerAppNo
        #         analysis_data_bak['delete_set'] = True
        #         logger.info(
        #             'end investor-save&member-save:product_id=%s analysis_data_bak=%s ' % (name, analysis_data_bak))
        #         logger.info(
        #             'end investor-save&member-save:product_id=%s parameters=%s ' % (name, json.loads(parameters)))
        #
        #     # 针对成员的删除
        #     elif 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_delete_member' in to_server:
        #         from urllib import parse
        #         logger.info('start member-delete:product_id=%s' % (name))
        #         params = parse.parse_qs(parse.urlparse(to_server).query)
        #         gdNo = params.get('id', [])[0]
        #         analysis_data_bak['customer_id'] = gdNo
        #         analysis_data_bak['delete_set'] = True
        #         logger.info(
        #             'end member-delete:product_id=%s analysis_data_bak=%s ' % (name, analysis_data_bak))
        #         logger.info(
        #             'end member-delete:product_id=%s parameters=%s ' % (name, json.loads(parameters)))
        #
        #     # 针对其他的form的保存，前提是appNo对应apply_form已经存在库里
        #     else:
        #         logger.info('start others-save:product_id=%s' % (name))
        #         yctAppNo = parameters_dict.get("yctAppNo", '') or parameters_dict.get("yctSocialUnit.yctAppNo", '')
        #         registerAppNo = parameters_dict.get("registerAppNo", '') or parameters_dict.get(
        #             'appNo') or parameters_dict.get('etpsMember.appNo')
        #
        #         if yctAppNo or registerAppNo:
        #             if r.get(yctAppNo):
        #                 analysis_data_bak['registerAppNo'] = ''
        #                 analysis_data_bak['yctAppNo'] = yctAppNo
        #                 analysis_data_bak['etpsName'] = r.get(yctAppNo).decode(encoding='utf-8') if isinstance(
        #                     r.get(yctAppNo),
        #                     bytes) else r.get(
        #                     yctAppNo)
        #             elif r.get(registerAppNo):
        #                 analysis_data_bak['yctAppNo'] = ''
        #                 analysis_data_bak['registerAppNo'] = registerAppNo
        #                 analysis_data_bak['etpsName'] = r.get(registerAppNo).decode(encoding='utf-8') if isinstance(
        #                     r.get(registerAppNo), bytes) else r.get(registerAppNo)
        #         logger.info(
        #             'end others-save:product_id=%s analysis_data_bak=%s ' % (name, analysis_data_bak))
        #         logger.info(
        #             'end others-save:product_id=%s parameters=%s ' % (name, json.loads(parameters)))
        # else: #处理 analysis_data_bak
        #     logger.info('product_id=%s' % (name))
        #     logger.info('analysis_data_bak=%s' % analysis_data_bak)
        #     logger.info(
        #         'product_id=%s parameters=%s ' % (name, parameters_dict))

        ###########end analysis###########
        ###########database###########
        save_to_analysis = Save_to_sql('yctformdata_request')
        # if page_name:
        #     if analysis_data_bak:
        #         is_del = analysis_data_bak.pop('delete_set')
        #         if is_del:  # 判断是否删除记录
        #             save_to_analysis.del_set(analysis_data_bak)
        #         else:
        #             save_to_analysis.insert_new(analysis_data_bak)
        # else:
        save_to_analysis.insert_new(analysis_data_bak)
        ####################################

    def responseheaders(self, flow: mitmproxy.http.HTTPFlow):
        """
            HTTP response headers were successfully read. At this point, the body
            is empty.
        """
        '''读取响应头内容'''

    def response(self, flow: mitmproxy.http.HTTPFlow):
        """
            The full HTTP response has been read.
        """
        # response_header = eval(dict(flow.response.headers)['response_header'])
        # # '''解码图片'''
        # # if flow.response.headers['Content-Type'].startswith('image/'):
        # #     with open(r'C:\Users\xh\proxy_yct\csdn-kf.png', 'wb') as f:
        # #         f.write(flow.response.content)
        # connect = filter_info['http_connect']
        # data_dict = {}
        # for i in connect:
        #    if i in flow.request.host:
        #        data_dict = self.yct_dealdatabag(flow)
        #        break
        #    else:
        if 'yct.sh' not in flow.request.url:
            return
        data_dict = self.other_dealdatabag(flow)
        #        break
        pickled = pickle.dumps(data_dict)
        data_str = str(pickled)

        self.run_celery(data_str)

    def other_dealdatabag(self,flow):
        data_bag = {}
        # data_bag['client_address'] = flow.client_conn.address
        data_bag['request'] = flow.request
        data_bag['time_circle'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data_bag['web_name'] = flow.request.host
        # data_bag['refer']=flow.request.headers.get('Referer','')
        data_bag['to_server'] = flow.request.url
        data_bag['response'] = flow.response
        data_bag['product_id'] = flow.request.product_id
        return data_bag

    def yct_dealdatabag(self,flow):
        data_bag = {}
        # data_bag['client_address'] = flow.client_conn.address
        data_bag['request'] = flow.request
        data_bag['time_circle'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data_bag['web_name'] = 'yct'
        # data_bag['refer']=flow.request.headers.get('Referer','')
        data_bag['to_server'] = flow.request.url
        data_bag['response'] = flow.response
        # print(data_bag)
        return data_bag


    def run_celery(self,data_str):
        #这个地方调用任务to_product
        handle_data(data_str)
        # folder=open(r'D:\data_bag_pickle\{}.pkl'.format(time.time()),mode='wb')
        # pickle.dump(data_bag,folder)
        # folder.close()

        # print(res)


    def error(self, flow: mitmproxy.http.HTTPFlow):
        """
            An HTTP error has occurred, e.g. invalid server responses, or
            interrupted connections. This is distinct from a valid server HTTP
            error response, which is simply a response with an HTTP error code.
        """

    # TCP lifecycle
    def tcp_start(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has started.
        """

    def tcp_message(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has received a message. The most recent message
            will be flow.messages[-1]. The message is user-modifiable.
        """

    def tcp_error(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP error has occurred.
        """

    def tcp_end(self, flow: mitmproxy.tcp.TCPFlow):
        """
            A TCP connection has ended.
        """

    # Websocket lifecycle
    def websocket_handshake(self, flow: mitmproxy.http.HTTPFlow):
        """
            Called when a client wants to establish a WebSocket connection. The
            WebSocket-specific headers can be manipulated to alter the
            handshake. The flow object is guaranteed to have a non-None request
            attribute.
        """

    def websocket_start(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has commenced.
        """

    def websocket_message(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            Called when a WebSocket message is received from the client or
            server. The most recent message will be flow.messages[-1]. The
            message is user-modifiable. Currently there are two types of
            messages, corresponding to the BINARY and TEXT frame types.
        """

    def websocket_error(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has had an error.
        """

    def websocket_end(self, flow: mitmproxy.websocket.WebSocketFlow):
        """
            A websocket connection has ended.
        """

    # Network lifecycle
    def clientconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        """
            A client has connected to mitmproxy. Note that a connection can
            correspond to multiple HTTP requests.
        """

    def clientdisconnect(self, layer: mitmproxy.proxy.protocol.Layer):
        """
            A client has disconnected from mitmproxy.
        """

    def serverconnect(self, conn: mitmproxy.connections.ServerConnection):
        """
            Mitmproxy has connected to a server. Note that a connection can
            correspond to multiple requests.
        """

    def serverdisconnect(self, conn: mitmproxy.connections.ServerConnection):
        """
            Mitmproxy has disconnected from a server.
        """

    def next_layer(self, layer: mitmproxy.proxy.protocol.Layer):
        """
            Network layers are being switched. You may change which layer will
            be used by returning a new layer object from this event.
        """

    # General lifecycle
    def configure(self, updated: typing.Set[str]):
        """
            Called when configuration changes. The updated argument is a
            set-like object containing the keys of all changed options. This
            event is called during startup with all options in the updated set.
        """

    def done(self):
        """
            Called when the addon shuts down, either by being removed from
            the mitmproxy instance, or when mitmproxy itself shuts down. On
            shutdown, this event is called after the event loop is
            terminated, guaranteeing that it will be the final event an addon
            sees. Note that log handlers are shut down at this point, so
            calls to log functions will produce no output.
        """

    def load(self, entry: mitmproxy.addonmanager.Loader):
        """
            Called when an addon is first loaded. This event receives a Loader
            object, which contains methods for adding options and commands. This
            method is where the addon configures itself.
        """

    def log(self, entry: mitmproxy.log.LogEntry):
        """
            Called whenever a new log entry is created through the mitmproxy
            context. Be careful not to log from this event, which will cause an
            infinite loop!
        """

    def running(self):
        """
            Called when the proxy is completely up and running. At this point,
            you can expect the proxy to be bound to a port, and all addons to be
            loaded.
        """

    def update(self, flows: typing.Sequence[mitmproxy.flow.Flow]):
        """
            Update is called when one or more flow objects have been modified,
            usually from a different addon.
        """
