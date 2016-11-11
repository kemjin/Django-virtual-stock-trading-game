from django.conf.urls import url

#from . import views
#from sleipnir.views import sleipnir_test_function
from sleipnir.views import *


urlpatterns = [
#    url(r'^$', views.index, name='index'),
#    url(r'^sleipnir_stock_price', sleipnir_test_function),
    url(r'^sleipnir_main', sleipnir_main),
    url(r'^sleipnir_total_perf', sleipnir_total_perf),
    url(r'^sleipnir_sell', sleipnir_sell),    
    url(r'^sleipnir_sold', sleipnir_sold),
    url(r'^sleipnir_holding_status', sleipnir_holding_status),    
    url(r'^sleipnir_purchase', sleipnir_purchase),
    url(r'^sleipnir_new_trade', sleipnir_new_trade),
]
