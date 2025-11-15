#render:HTMLを表示 redirect:アカウント登録完了後ログイン画面やホーム画面に移動するため
from django.shortcuts import render, redirect

#RegisterForm:フォームクラスを使うため(forms.pyで作成したもの)
from .forms import RegisterForm

#登録完了後、「登録が成功しました」などのメッセージ表示するなら
from django.contribd import messages

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
    return render(request, 'register.html', {'form': form})