# Register your models here.

from collections import OrderedDict as SortedDict

# 修改模型显示顺序为注册顺序
from django.contrib import admin
from django.db.models import Sum, Q
from django.utils.text import capfirst

from app.models import Users, Goods, Orders, Pay, Address, Groups


def find_model_index(name):
    count = 0
    for model, model_admin in admin.site._registry.items():
        if capfirst(model._meta.verbose_name_plural) == name:
            return count
        else:
            count += 1
    return count


def index_decorator(func):
    def inner(*args, **kwargs):
        template_response = func(*args, **kwargs)
        for app in template_response.context_data['app_list']:
            app['models'].sort(key=lambda x: find_model_index(x['name']))
        return template_response

    return inner


registry = SortedDict()
registry.update(admin.site._registry)
admin.site._registry = registry
admin.site.index = index_decorator(admin.site.index)
admin.site.app_index = index_decorator(admin.site.app_index)


class UsersAdmin(admin.ModelAdmin):
    # 手机号 下单次数 下单金额 是否可开团 收货地址
    list_display = ('id', 'username', 'phone', 'group_permissions', 'orders_num', 'orders_price', 'address')
    list_editable = ['group_permissions']
    list_per_page = 5
    ordering = ('id',)
    search_fields = ('phone',)
    readonly_fields = ['username', 'phone']

    def orders_num(self, obj):
        orders_num = Orders.objects.filter(u_id=obj.id).count()
        if not orders_num:
            return 0
        return orders_num

    def orders_price(self, obj):
        orders_price = Orders.objects.filter(u_id=obj.id).aggregate(total_price=Sum('total_price'))
        if not orders_price['total_price']:
            return 0
        return orders_price['total_price']

    def address(self, obj):
        address = Address.objects.filter(Q(u_id=obj.id) & Q(address_status=1)).first()
        if not address:
            return '空'
        return address.address

    orders_num.short_description = '下单数量'
    orders_price.short_description = '下单价格'
    address.short_description = '收货地址'


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'img', 'old_price', 'sale_price')
    ordering = ('id',)
    search_fields = ('name',)


class OrdersAdmin(admin.ModelAdmin):
    # 单号、商品名称、商品价格、开团用户、参团用户、支付凭证、发起时间、开团时间、物流单号、完成时间、订单状态
    # initiator_id
    # participant_id
    list_editable = ['order_status']
    list_display = (
        'id', 'odd_id', 'goods_name', 'pay_img', 't_create', 'tracking_number', 't_delivery',
        'order_status', 'initiator', 'participant')
    search_fields = ('goods_name', 'order_status')

    def initiator(self, obj):
        group = Groups.objects.filter(id=obj.groups_id).first()
        if not group:
            return '空'
        return Users.objects.get(id=group.initiator_id).username

    initiator.short_description = '开团用户'

    def participant(self, obj):
        group = Groups.objects.filter(id=obj.groups_id).first()
        if not group:
            return '空'
        return Users.objects.get(id=group.participant_id).username

    participant.short_description = '参团用户'


class PayAdmin(admin.ModelAdmin):
    list_display = ('id', 'img')


# 支付管理
# class UsersAdmin(admin.ModelAdmin):
#     list_display = ('id',)
#

admin.site.register(Users, UsersAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Pay, PayAdmin)

admin.site.site_title = "商城后台管理"
admin.site.site_header = "商城后台管理"
