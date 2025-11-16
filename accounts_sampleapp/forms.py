#Djangoのフォーム機能を使うためインポート（入力欄、バリエーション、エラー管理、HTMLに表示など）
from django import forms
#ユーザーモデルを安全に取り出すための関数　get_user_modelで標準UserでもカスタムUserでも使用できる
from django.contrib.auth import get_user_model
#パスワードの英数字チェックに必要なモジュール
import re

#ファイル内でUserモデルを使いやすくする　Userモデルを取り出してUser変数に保存
User = get_user_model()

#アカウント登録フォーム
class RegisterForm(forms.Form): #password_confirmはDBに入らないため、forms.ModelFormではなくforms.Formを使用
    #name, email, password, password_confirmを入力してもらう
    name = forms.CharField(
        max_length=20,
        label="ユーザー名",
        widget=forms.TextInput(attrs={'placeholder': 'ユーザー名'})
    )
    email = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(attrs={'placeholder': 'xxx@example.com'})
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={'placeholder': '８文字以上の英数字'})
    )
    password_confirm = forms.CharField(
        label="パスワード（確認）",
        widget=forms.PasswordInput(attrs={'placeholder': 'もう一度入力'})
    )
    
    #nameの文字数チェック
    def clean_name(self):
        name = self.cleaned_data.get('name') #ユーザーが入力したnameの値をnameという変数に入れる
        if not name:  #nameが空やNoneの時
            raise forms.ValidationError('ユーザー名を入力してください')
        if not (1 <= len(name) <= 20):
            raise forms.ValidationError('ユーザー名は１文字以上２０文字以下で入力してください')
        #nameの重複チェック
        if User.objects.filter(username=name).exists():
            raise forms.ValidationError('このユーザー名は既に使われています')
        return name
    #passwordの長さ・英数字チェック
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('パスワードを入力してください')
        if len(password) < 8:
            raise forms.ValidationError('パスワードは8文字以上で入力してください')
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError('パスワードは英字と数字を含めてください')
        return password
    #passwordとpassword_confirmが一致するかチェック
    def clean_password_confirm(self):
        #入力された確認用パスワードを取得
        password_confirm = self.cleaned_data.get('password_confirm')
        #未入力チェック
        if not password_confirm:
            raise forms.ValidationError('確認用パスワードを入力してください')
        
        #元のpasswordの値を取得
        password = self.cleaned_data.get('password')
        #passwordとpassword_confirmが一致しているかチェック
        if password and password_confirm != password:
            raise forms.ValidationError('パスワードが一致しません')
        
        #問題なければユーザーを作成して保存する
        return password_confirm


