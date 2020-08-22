import datetime
import json
import logging
import random

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Img, Goods, Users, Address, Groups, Orders, PhoneCode, Pay
from app.serializers import GoodsSerializer, AddressSetSerializer, AddressGetSerializer, GroupsSerializer, \
    OrdersGetSerializer, OOrdersGetSerializer, OrdersSetSerializer, UsersSerializer

logger = logging.getLogger('sc_log')


def get_sms_code(num):
    code = ''
    for i in range(num):
        code += str(random.randint(0, 9))
    return code


def send_sms(template, phone):
    client = AcsClient('LTAI4G1ifFzikkSRBEjJ1vmd', '2QjFzxrUCO0RWDnb6buX745admKabn', 'default')

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('http')  # https | http 注意当项目发布到服务器上需要修改协议
    request.set_version('2017-05-25')

    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "default")

    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', "对折正品百货")
    request.add_query_param('TemplateCode', "SMS_189520572")
    request.add_query_param('TemplateParam', f"{template}")
    response = client.do_action_with_exception(request)
    return response


# sms
class SmsAPIView(APIView):
    def post(self, request):
        response = {'status': 900, 'message': 'Sms Send Success'}
        try:
            phone = request.data.get('phone')

            sms_code = get_sms_code(4)
            template = {
                'code': sms_code
            }
            res = send_sms(template, phone=phone)
            res_dict = json.loads(res)
            if res_dict.get('Message') == 'OK' and res_dict.get('Code') == 'OK':
                phone_obj = PhoneCode.objects.filter(phone=phone).first()
                if phone_obj:
                    phone_obj.sms_code = sms_code
                    phone_obj.save()

                else:
                    PhoneCode.objects.create(phone=phone, sms_code=sms_code)
                response['sms_code'] = sms_code
                return Response(response)
            else:
                response['status'] = 901
                response['message'] = 'Sms Send Fail'
                return Response(response)

        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('POST: sms, ERROR: {}'.format(e))
            return Response(response)


def get_t_node():
    date_now = datetime.datetime.now()
    t_expiration = datetime.timedelta(minutes=5)
    t_node = date_now - t_expiration
    return t_node


# login
class LoginAPIView(APIView):
    def post(self, request):

        try:
            response = {'status': 900, 'message': 'Login Success'}
            phone = request.data.get('phone')
            sms_code = request.data.get('sms_code')

            phone_obj = PhoneCode.objects.get(phone=phone)
            t_node = get_t_node()
            if t_node <= phone_obj.t_create:
                if sms_code == phone_obj.sms_code:
                    users = Users.objects.get(phone=phone)
                    users_class = UsersSerializer(users)
                    response['data'] = users_class.data
                    return Response(response)
                else:
                    response = {'status': 901, 'message': 'Sms Code Fail'}
                    return Response(response)

            else:
                response = {'status': 901, 'message': 'Verification code invalidation'}
                return Response(response)

        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('POST: login, ERROR: {}'.format(e))
            return Response(response)


# register
class RegisterAPIView(APIView):

    def post(self, request):

        try:
            response = {'status': 900, 'message': 'Register Success'}
            username = request.data.get('username')
            phone = request.data.get('phone')
            sms_code = request.data.get('sms_code')
            user = Users.objects.filter(phone=phone)

            if user:
                response['status'] = 905
                response['message'] = 'User already exists'
                return Response(response)

            phone_obj = PhoneCode.objects.get(phone=phone)
            t_node = get_t_node()
            if t_node <= phone_obj.t_create:
                if sms_code == phone_obj.sms_code:

                    u = Users.objects.create(username=username, phone=phone)
                    users_class = UsersSerializer(u)
                    response['data'] = users_class.data
                    return Response(response)
                else:
                    response = {'status': 901, 'message': 'Sms Code Fail'}
                    return Response(response)

            else:
                response = {'status': 901, 'message': 'Verification code invalidation'}
                return Response(response)

        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('POST: login, ERROR: {}'.format(e))
            return Response(response)


# search
class GoodsSearchAPIView(APIView):
    def get(self, request):
        try:
            response = {'status': 900, 'message': 'Success'}
            try:
                skip = int(request.query_params.get('skip'))
                limit = int(request.query_params.get('limit'))
            except TypeError as e:
                response = {'status': 903, 'message': 'Fail', 'error': 'Required parameter missing'}
                logger.error('GET: search, ERROR: {}'.format(e))
                return Response(response)
            skipend = skip + limit
            keyword = request.query_params.get('keyword')
            if keyword:
                goods = Goods.objects.filter(name__contains=keyword)[skip:skipend]
                goods_class = GoodsSerializer(instance=goods, many=True)
                response['data'] = goods_class.data
                return Response(response)
            else:
                goods = Goods.objects.all()[skip:skipend]
                goods_class = GoodsSerializer(instance=goods, many=True)
                response['data'] = goods_class.data
                return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: search, ERROR: search请求Fail:{}'.format(e))
            return Response(response)


# Goods
class GoodsAPIView(APIView):
    def get(self, request):
        try:
            response = {'status': 900, 'message': 'Success'}
            try:
                skip = int(request.query_params.get('skip'))
                limit = int(request.query_params.get('limit'))
            except TypeError as e:
                response = {'status': 903, 'message': 'Fail', 'error': 'Required parameter missing'}
                logger.error('GET: goods, ERROR: {}'.format(e))
                return Response(response)
            skipend = skip + limit
            goods = Goods.objects.all()[skip:skipend]
            goods_class = GoodsSerializer(instance=goods, many=True)
            response['data'] = goods_class.data
            return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: goods, ERROR: goods请求Fail:{}'.format(e))
            return Response(response)


class OGoodsAPIView(APIView):

    def get(self, request, pk):
        try:
            response = {'status': 900, 'message': 'Success'}
            goods = Goods.objects.get(id=pk)
            if goods:
                goods_class = GoodsSerializer(goods)
                try:
                    skip = int(request.query_params.get('skip'))
                    limit = int(request.query_params.get('limit'))
                except TypeError as e:
                    response = {'status': 903, 'message': 'Fail', 'error': 'Required parameter missing'}
                    logger.error('GET: goods/id, ERROR: {}'.format(e))
                    return Response(response)
                skipend = skip + limit
                groups = Groups.objects.filter(Q(goods_id=goods.id) & Q(groups_status=0))[skip:skipend]
                groups_class = GroupsSerializer(instance=groups, many=True)

                response['data'] = goods_class.data
                response['data']['groups'] = groups_class.data
                return Response(response)
            else:
                response = {'status': 904, 'message': 'Not exist'}
                return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: goods, ERROR: {}'.format(e))
            return Response(response)


# address
class AddressAPIView(APIView):
    def get(self, request):

        try:
            response = {'status': 900, 'message': 'Success'}
            try:
                skip = int(request.query_params.get('skip'))
                limit = int(request.query_params.get('limit'))
            except TypeError as e:
                response = {'status': 903, 'message': 'Fail', 'error': 'Required parameter missing'}
                logger.error('GET: address, ERROR: {}'.format(e))
                return Response(response)
            skipend = skip + limit

            u_id = request.query_params.get('u_id')

            address = Address.objects.filter(u_id=u_id)[skip:skipend]

            address_class = AddressGetSerializer(instance=address, many=True)

            response['data'] = address_class.data

            return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: address, ERROR: address请求Fail:{}'.format(e))
            return Response(response)

    def post(self, request):

        try:
            response = {'status': 900, 'message': 'Success'}
            address = AddressSetSerializer(data=request.data)
            if address.is_valid():
                if request.data['address_status'] == '1':
                    Address.objects.filter(u_id=request.data['u_id']).update(address_status=0)
                address.save()
                response["message"] = "Success"
                response["data"] = address.data
                return Response(response)
            else:
                response["status"] = 901
                response["message"] = "Address create Fail"
                response["error"] = address.errors
                return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('POST: address, ERROR: address请求Fail:{}'.format(e))
            return Response(response)


class OAddressAPIView(APIView):
    def delete(self, request, pk):
        try:
            response = {'status': 900, 'message': 'Delete Address Success'}
            address = Address.objects.filter(id=pk).first()
            if address:
                address.delete()
                return Response(response)
            else:
                response['status'] = 904
                response['message'] = 'Not exist'
                return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('DELETE: address, ERROR: address请求Fail:{}'.format(e))
            return Response(response)

    def put(self, request, pk):
        try:
            response = {'status': 900, 'message': 'Success'}
            old_address = Address.objects.filter(id=pk).first()
            if old_address:
                new_address = AddressSetSerializer(instance=old_address, data=request.data, partial=False)
                if new_address.is_valid():
                    if request.data['address_status'] == '1':
                        Address.objects.filter(u_id=request.data['u_id']).update(address_status=0)
                    new_address.save()
                    response['data'] = new_address.data
                    return Response(response)
                else:
                    response["status"] = 901
                    response["message"] = "Address update Fail"
                    response["error"] = new_address.errors
                    return Response(response)
            else:
                response['status'] = 904
                response['message'] = 'Not exist'
                return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('PUT: address, ERROR: address请求Fail:{}'.format(e))
            return Response(response)


def tid_maker():
    return '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())


# 订单号生成
def get_odd():
    odd_id = tid_maker()
    if Orders.objects.filter(odd_id=odd_id):
        return get_odd()
    return odd_id


# orders
class OrdersAPIView(APIView):
    def get(self, request):
        # 0 未付款  1 已付款  已送达  3全部
        response = {'status': 900, 'message': 'Success'}

        try:

            try:
                skip = int(request.query_params.get('skip'))
                limit = int(request.query_params.get('limit'))
                action = int(request.query_params.get('action'))
            except TypeError as e:
                response = {'status': 903, 'message': 'Fail', 'error': 'Required parameter missing'}
                logger.error('GET: orders, ERROR: {}'.format(e))
                return Response(response)
            skipend = skip + limit
            u_id = request.query_params['u_id']
            if action == 0:
                orders = Orders.objects.filter(Q(u_id=u_id) & Q(order_status=0))[skip:skipend]
                orders_class = OrdersGetSerializer(instance=orders, many=True)
                response['data'] = orders_class.data
                return Response(response)

            elif action == 1:
                orders = Orders.objects.filter(Q(u_id=u_id) & Q(order_status=1))[skip:skipend]
                orders_class = OrdersGetSerializer(instance=orders, many=True)
                response['data'] = orders_class.data
                return Response(response)
            elif action == 2:
                orders = Orders.objects.filter(Q(u_id=u_id) & Q(order_status=2))[skip:skipend]
                orders_class = OrdersGetSerializer(instance=orders, many=True)
                response['data'] = orders_class.data
                return Response(response)
            elif action == 3:
                orders = Orders.objects.filter(u_id=u_id)[skip:skipend]
                orders_class = OrdersGetSerializer(instance=orders, many=True)
                response['data'] = orders_class.data
                return Response(response)
            else:
                response = {'status': 902, 'message': 'Invalid Operation'}
                return Response(response)

        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: orders, ERROR: {}'.format(e))
            return Response(response)

    def post(self, request):
        try:
            response = {'status': 900, 'message': 'Success'}
            # 订单号
            odd_id = get_odd()
            action = int(request.data.get('action'))
            # 0 开团  1参团

            if action == 0:
                groups = Groups.objects.create(goods_id=request.data['goods_id'], initiator_id=request.data['u_id'])
                _mutable = request.data._mutable
                request.data._mutable = True
                request.data['odd_id'] = odd_id
                request.data['groups_id'] = groups.id
                request.data._mutable = _mutable
                orders = OrdersSetSerializer(data=request.data)
                if orders.is_valid():
                    orders.save()
                    response['data'] = orders.data
                    return Response(response)
            elif action == 1:
                groups_id = request.data['groups_id']
                groups = Groups.objects.get(id=groups_id)
                groups.participant_id = request.data['u_id']
                groups.groups_status = 1
                groups.save()
                _mutable = request.data._mutable
                request.data._mutable = True
                request.data['odd_id'] = odd_id
                request.data['groups_id'] = groups_id
                request.data._mutable = _mutable
                orders = OrdersSetSerializer(data=request.data)
                if orders.is_valid():
                    orders.save()

                    response['data'] = orders.data

                    return Response(response)
            else:
                response = {'status': 902, 'message': 'Invalid Operation'}
                return Response(response)

        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('POST: orders, ERROR: {}'.format(e))
            return Response(response)


class OOrdersAPIView(APIView):
    def get(self, request, pk):

        try:
            response = {'status': 900, 'message': 'Success'}
            orders = Orders.objects.get(id=pk)
            orders_class = OOrdersGetSerializer(orders)
            response['data'] = orders_class.data
            return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: orders, ERROR: {}'.format(e))
            return Response(response)


# 支付凭证
class Pay_ProofAPIView(APIView):
    def post(self, request):
        try:
            response = {'status': 900, 'message': 'Upload Success'}
            Orders.objects.filter(id=request.data['order_id']).update(pay_img=request.data['pay_img'])
            return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('POST: pay-proof, ERROR: {}'.format(e))
            return Response(response)


# 上传图片
def upload_img(request):
    if request.method == 'POST':
        response = {'status': '', 'message': ''}
        try:
            new_img = Img(
                img=request.FILES.get('img'),
                name=request.FILES.get('img').name
            )
            new_img.save()
            response['status'] = 900
            response['message'] = 'Success'
            response['img_url'] = 'http://101.201.145.241' + new_img.img.url

            return JsonResponse(response, json_dumps_params={'ensure_ascii': False}, )
        except Exception as e:
            logger.error('POST: upload-img, ERROR: upload-img请求Fail:{}'.format(e))
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            return JsonResponse(response, json_dumps_params={'ensure_ascii': False}, )

    response = {'status': 900, 'message': 'get-ok'}
    return JsonResponse(response)


class Pay_QrcodefAPIView(APIView):
    def get(self, request):
        try:
            response = {'status': 900, 'message': 'Success'}
            qrcode = Pay.objects.all().first()
            if qrcode:
                qrcode_url = 'http://101.201.145.241' + qrcode.img.url
                response['qrcode_url'] = qrcode_url
                return Response(response)
            else:
                response['status'] = 904
                response['message'] = 'Not exist'
                return Response(response)
        except Exception as e:
            response = {'status': 901, 'message': 'Fail', 'error': str(e)}
            logger.error('GET: pay-qrcode, ERROR: {}'.format(e))
            return Response(response)
