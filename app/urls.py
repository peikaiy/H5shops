from django.urls import re_path, path

from app import api

app_name = 'app'
urlpatterns = [

    # sms
    re_path(r'^sms$', api.SmsAPIView.as_view()),
    # login
    re_path(r'^login$', api.LoginAPIView.as_view()),
    # register
    re_path(r'^register$', api.RegisterAPIView.as_view()),


    # goods
    re_path(r'^goods$', api.GoodsAPIView.as_view()),
    re_path(r'^goods/(?P<pk>\d+)$', api.OGoodsAPIView.as_view()),
    # goods search
    re_path(r'^goods/search$', api.GoodsSearchAPIView.as_view()),

    # address
    re_path(r'^address$', api.AddressAPIView.as_view()),
    re_path(r'^address/(?P<pk>\d+)$', api.OAddressAPIView.as_view()),

    # orders
    re_path(r'^orders$', api.OrdersAPIView.as_view()),
    re_path(r'^orders/(?P<pk>\d+)$', api.OOrdersAPIView.as_view()),

    # 支付凭证 凭证
    re_path(r'^orders/pay-proof$', api.Pay_ProofAPIView.as_view()),
    #平台收款二维码
    re_path(r'^pay-qrcode$', api.Pay_QrcodefAPIView.as_view()),
    # 图片上传
    re_path(r'^upload-img$', api.upload_img),

]
