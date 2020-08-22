from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models


# Create your models here.


# 上传图片
class Img(models.Model):
    img = models.ImageField(upload_to='imgs')
    name = models.CharField(max_length=256)

    class Meta:
        db_table = 'Sc_imgs'


group_permissions = (
    (0, '否'),
    (1, '是'),
)


# 用户
class Users(models.Model):
    username = models.CharField(max_length=128, verbose_name="用户名")
    phone = models.CharField(unique=True, max_length=16, verbose_name="手机号")
    group_permissions = models.IntegerField(choices=group_permissions, default=0, verbose_name="开团权限")

    class Meta:
        db_table = 'Sc_users'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name


# 验证码
class PhoneCode(models.Model):
    phone = models.CharField(max_length=16, unique=True)
    sms_code = models.CharField(max_length=64)
    t_create = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Sc_phone_code'


address_status = (
    (0, "普通"),
    (1, "默认")
)


# 收货地址
# 用户  收货人 收货电话 收货地址
class Address(models.Model):
    u_id = models.PositiveIntegerField()
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=64)
    address = models.CharField(max_length=512)
    address_status = models.PositiveIntegerField(choices=address_status, default=0)

    class Meta:
        db_table = 'Sc_address'
        ordering = ('-address_status',)


# 商品
# 商品名 图片  原价  拼团价  已拼人数
class Goods(models.Model):
    name = models.CharField(max_length=256, verbose_name="商品名")
    img = models.ImageField(upload_to='goods',  verbose_name="商品图")
    old_price = models.FloatField(verbose_name="原价")
    sale_price = models.FloatField(verbose_name="拼团价")
    # already_num = models.PositiveIntegerField(default=0, verbose_name="已拼团人数")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Sc_goods'
        verbose_name = '商品管理'
        verbose_name_plural = verbose_name


groups_status = (
    (0, '在团'),
    (1, '成功')
)


# 拼团
# 商品id 开团者id  参团者id   拼团状态
class Groups(models.Model):
    goods_id = models.PositiveIntegerField()
    initiator_id = models.PositiveIntegerField()
    participant_id = models.PositiveIntegerField(null=True)
    groups_status = models.PositiveIntegerField(choices=groups_status, default=0)

    class Meta:
        db_table = 'Sc_groups'


order_status = (
    (0, '未付款'),
    (1, '已付款'),
    (2, '已送达'),
)


# 订单
# 订单号 用户id   商品名 商品图片 价格 数量 总价  订单状态(未付款，已付款，已送达) 收货地址信息 订单备注 快递单号 支付凭证
# 订单创建时间  付款时间 发货时间  送达时间
class Orders(models.Model):
    odd_id = models.CharField(unique=True, max_length=128, verbose_name="订单号")
    u_id = models.PositiveIntegerField()
    groups_id = models.PositiveIntegerField()
    goods_id = models.PositiveIntegerField()

    goods_name = models.CharField(max_length=256, verbose_name="商品名称")
    goods_img = models.CharField(max_length=256)
    goods_price = models.FloatField()
    goods_num = models.PositiveIntegerField()
    total_price = models.FloatField(verbose_name="商品价格")
    order_status = models.PositiveIntegerField(choices=order_status, default=0, verbose_name="订单状态")
    address_name = models.CharField(max_length=128)
    address_phone = models.CharField(max_length=11)
    address_address = models.CharField(max_length=512)
    address_note = models.CharField(max_length=512, null=True)
    tracking_number = models.CharField(max_length=128, null=True, verbose_name="快递单号")
    pay_img = models.CharField(max_length=128, null=True, verbose_name="支付凭证")

    t_create = models.DateTimeField(auto_now_add=True, verbose_name="开团时间")
    t_pay = models.DateTimeField(null=True)
    t_send = models.DateTimeField(null=True)
    t_delivery = models.DateTimeField(null=True, verbose_name="送达时间")

    class Meta:
        db_table = 'Sc_orders'
        verbose_name = '订单管理'
        verbose_name_plural = verbose_name


class Pay(models.Model):
    img = models.ImageField(upload_to='pay', verbose_name="支付二维码")

    class Meta:
        db_table = 'Sc_pay'
        verbose_name = '支付管理'
        verbose_name_plural = verbose_name
