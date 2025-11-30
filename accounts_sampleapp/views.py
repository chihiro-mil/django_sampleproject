#render:HTMLを表示 redirect:アカウント登録完了後ログイン画面やホーム画面に移動するため
from django.shortcuts import render, redirect

#RegisterForm:フォームクラスを使うため(forms.pyで作成したもの)
from .forms import RegisterForm

#ユーザーモデルを安全に取り出すための関数　get_user_modelで標準UserでもカスタムUserでも使用できる
from django.contrib.auth import get_user_model

#登録完了後、「登録が成功しました」などのメッセージ表示するなら
from django.contrib import messages

#ログイン画面の存在するユーザー確認機能とログイン機能を借りる
from django.contrib.auth import authenticate, login

#ログイン画面のフォームを使うため(forms.pyで作成したもの)
from .forms import LoginForm

#ログインしている状態の時に開けるように制限
from django.contrib.auth.decorators import login_required

#ユーザー名変更のフォームを使うため
from .forms import ChangeUsernameForm

#メールアドレス変更のフォームを使うため
from .forms import ChangeEmailForm

#パスワード変更後もログイン状態を維持する
from django.contrib.auth import update_session_auth_hash

#メールアドレス変更のフォームを使うため ChangePasswordFormだとDjangoの標準の名前と被るため
from .forms import CustomPasswordChangeForm



#ファイル内でUserモデルを使いやすくする　Userモデルを取り出してUser変数に保存
User = get_user_model()

#アカウント登録画面のビュー
def register_view(request):
    #POSTかGETか判定する
    if request.method == 'POST':
        #POSTの場合、送られてきた値を使ってフォーム作る
        form = RegisterForm(request.POST)
        #フォームをバリエーションする
        if form.is_valid():
            #OKならユーザーを保存して、ホーム画面へリダイレクト
            #カスタムUserをviewsでも安全に取り出す
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            User.objects.create_user(
                name=name,
                email=email,
                password=password,
            )
            return redirect('accounts_sampleapp:login') #一旦ログイン画面に設定
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
                return redirect('accounts_sampleapp:account_settings')
            #認証に失敗したらフォーム全体のエラーとして追加
            else:
                form.add_error(None, "メールアドレスまたはパスワードが間違っています")
    #GETの場合は空フォームを作成
    else:
        form = LoginForm()
    
    #login.htmlにformを渡して表示
    return render(request, 'accounts_sampleapp/login.html', {'form': form})

#アカウント設定トップ画面
@login_required
def account_settings_view(request):
    #ログイン中のユーザー情報をテンプレートへ渡す
    context = {
        'user': request.user #usernameやemailが使える
    }
    return render(request, 'accounts_sampleapp/account_settings.html', context)

#ユーザー名変更画面
@login_required
def change_username_view(request):
    if request.method == 'POST': #POSTの時
        form = ChangeUsernameForm(request.POST, instance=request.user) #POSTデータをフォームに入れる、instance=request.userを指定するとユーザー情報を置き換えるフォームになる
        if form.is_valid(): #フォームのバリエーション
            form.save() #ユーザー名を保存（Userモデルを更新）
            request.user.refresh_from_db() #保存された最新のユーザー情報をrequest.userに反映
            messages.success(request, 'ユーザー名を変更しました')
            return redirect('accounts_sampleapp:account_settings')
    else: #GETの時
        form = ChangeUsernameForm() #初期表示　今のユーザー名を初期値に入れたフォームを作る
    return render(request, 'accounts_sampleapp/change_username.html', {'form': form}) #テンプレートにフォームを渡す


#メールアドレス変更画面
@login_required
def change_email_view(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.refresh_from_db()
            messages.success(request, 'メールアドレスを変更しました')
            return redirect('accounts_sampleapp:account_settings')
    else:
        form = ChangeEmailForm()
    return render(request, 'accounts_sampleapp/change_email.html', {'form': form})


#パスワード変更画面
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST) #user=request.userでログインしているユーザーをフォームに渡す、data=request.POSTで画面で入力された現在のパスワード、新しいパスワード、確認用新しいパスワードをチェック
        if form.is_valid():
            user = form.save() #現在のパスワード、新しいパスワードと確認用新しいパスワード、パスワードが安全なルールを満たす時にform.save()が動く
            update_session_auth_hash(request, user) #update_session_auth_hashでパスワードを変更した後もログアウトされないように
            messages.success(request, 'パスワードを変更しました')
            return redirect('accounts_sampleapp:account_settings')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'accounts_sampleapp/change_password.html', {'form': form})