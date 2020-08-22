from django.db.models import Q
from rest_framework import serializers

from app.models import Goods, Address, Users, Groups, Orders


class UsersSerializer(serializers.ModelSerializer):
    """用户数据序列化器"""

    class Meta:
        model = Users

        fields = '__all__'



class GoodsSerializer(serializers.ModelSerializer):
    """商品数据序列化器"""
    already_num = serializers.SerializerMethodField(label='已拼团')
    goods_img = serializers.SerializerMethodField(label='商品图片')

    class Meta:
        model = Goods

        fields = ('id', 'name', 'goods_img',  'old_price', 'sale_price', 'already_num')

    def get_already_num(self, obj):
        already_num = Orders.objects.filter(Q(goods_id=obj.id) & Q(order_status=1)).count()
        return already_num

    def get_goods_img(self, obj):
        goods_img = 'http://101.201.145.241' + obj.img.url
        return goods_img


class GroupsSerializer(serializers.ModelSerializer):
    """拼团数据序列化器"""

    initiator = serializers.SerializerMethodField(label='发起人')

    class Meta:
        model = Groups
        fields = ('initiator', 'id')

    def get_initiator(self, obj):
        initiator = Users.objects.get(id=obj.initiator_id).username
        return initiator


class AddressSetSerializer(serializers.ModelSerializer):
    """收货地址存储序列化器"""

    class Meta:
        model = Address

        fields = '__all__'


class AddressGetSerializer(serializers.ModelSerializer):
    """收货地址查询序列化器"""

    class Meta:
        model = Address

        fields = '__all__'


class OrdersSetSerializer(serializers.ModelSerializer):
    """订单存储序列化器"""
    t_create = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    t_pay = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    t_send = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    t_delivery = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    order_status = serializers.CharField(read_only=True, source='get_order_status_display')

    class Meta:
        model = Orders
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['t_pay']:
            data['t_pay'] = ""
        if not data['t_send']:
            data['t_send'] = ""
        if not data['t_delivery']:
            data['t_delivery'] = ""
        if not data['address_note']:
            data['address_note'] = ""
        if not data['tracking_number']:
            data['tracking_number'] = ""
        if not data['pay_img']:
            data['pay_img'] = ""

        return data


class OrdersGetSerializer(serializers.ModelSerializer):
    """订单查询序列化器"""

    order_status = serializers.CharField(read_only=True, source='get_order_status_display')

    class Meta:
        model = Orders
        fields = ('id', 'goods_name', 'goods_img', 'goods_price', 'goods_num', 'order_status')


class OOrdersGetSerializer(serializers.ModelSerializer):
    """订单查询序列化器"""
    t_create = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    t_pay = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    t_send = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    t_delivery = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    order_status = serializers.CharField(read_only=True, source='get_order_status_display')

    class Meta:
        model = Orders
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['t_create']:
            data['t_create'] = ""
        if not data['t_pay']:
            data['t_pay'] = ""
        if not data['t_send']:
            data['t_send'] = ""
        if not data['t_delivery']:
            data['t_delivery'] = ""
        if not data['address_note']:
            data['address_note'] = ""
        if not data['tracking_number']:
            data['tracking_number'] = ""
        if not data['pay_img']:
            data['pay_img'] = ""

        return data
