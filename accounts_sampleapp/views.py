#render:HTMLを表示 redirect:アカウント登録完了後ログイン画面やホーム画面に移動するため
from django.shortcuts import render, redirect

#RegisterForm:フォームクラスを使うため(forms.pyで作成したもの)
from .forms import RegisterForm

#登録完了後、「登録が成功しました」などのメッセージ表示するなら
from django.contrib import messages

#ログイン画面の存在するユーザー確認機能とログイン機能を借りる
from django.contrib.auth import authenticate, login

#ログイン画面のフォームを使うため(forms.pyで作成したもの)
from .forms import LoginForm

#アカウント登録画面のビュー
def register_view(request):
    #POSTかGETか判定する
    if request.method == 'POST':
        #POSTの場合、送られてきた値を使ってフォーム作る
        form = RegisterForm(request.POST)
        #フォームをバリエーションする
        if form.is_valid():
            #OKならユーザーを保存して、ホーム画面へリダイレクト
            form.save()
            return redirect('home')
            #NGならエラー付きフォームをそのままテンプレートへ渡す
    #GETの時は空フォームを作る
    else:
        form = RegisterForm()
    #最後に register.htmlを表示してフォームを渡す
    return render(request, 'accounts_sampleapp/register.html', {'form': form})

#ログイン画面のビュー
def login_view(request):
    #POSTかGETか判定する
    if request.method == 'POST':
        #ユーザーが送信した値でLoginFormを作成
        form = LoginForm(request.POST)
        #フォーム全体のバリエーション（forms.pyのcleanが実行される）
        if form.is_valid():
            #バリエーションＯＫならフォームからemailとパスワード取り出す
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            #authenticate()で存在するユーザーか確認
            user = authenticate(request, email=email, password=password)
            
            #userがNoneではない→ログイン成功
            if user is not None:
                #loginを呼んでDjangoがログイン状態を作る
                login(request, user)
                #ログイン後にホーム画面へ移動
                return redirect('accounts_sampleapp:home')
            #認証に失敗したらフォーム全体のエラーとして追加
            else:
                form.add_error(None, "メールアドレスまたはパスワードが間違っています")
    #GETの場合は空フォームを作成
    else:
        form = LoginForm()
    
    #login.htmlにformを渡して表示
    return render(request, 'accounts_sampleapp/login.html', {'form': form})