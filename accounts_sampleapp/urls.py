#DjangoのURL設定に使う関数pathを使う定義
from django.urls import path
#（ . :同じ階層）同じ階層のviews.pyを読み込み
from . import views

app_name = 'accounts_sampleapp' #どの場所のurlか分かるように名前空間を定義（※変数ではない）


#path('URLの文字列', 呼び出す関数, name='名前'(テンプレで呼び出す専用の名前))
urlpatterns = [
    #path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
]
