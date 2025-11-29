#Djangoのフォーム機能を使うためインポート（入力欄、バリエーション、エラー管理、HTMLに表示など）
from django import forms
#ユーザーモデルを安全に取り出すための関数　get_user_modelで標準UserでもカスタムUserでも使用できる
from django.contrib.auth import get_user_model
#パスワードの英数字チェックに必要なモジュール
import re
#ログイン画面の存在するユーザー確認機能
from django.contrib.auth import authenticate

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
    
    def clean_email(self):
        email = self.changed_data.get('email')
        if not email:
            raise forms.ValidationError('メールアドレスを入力してください')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています')
        return email
    
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

#ログイン画面フォーム
#ログイン用のフォームクラスを定義
class LoginForm(forms.Form):
    #メールアドレスの入力欄
    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@example.com',
        })
    )
    #パスワードの入力欄
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'パスワード',
        })
    )
    
    #フォーム全体のチェック関数　emailとパスワードを入力した後、本当にそのユーザーが存在するか確認
    def clean(self):
        cleaned_data = super().clean() #既存のバリエーション結果を取得
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password) #authenticate()でDjangoにこのメールとパスワードユーザーは存在するか聞く　パスワードはDjangoが自動でハッシュ比較
            
            #Noneの時、全体のエラーとして追加
            if user is None:
                raise forms.ValidationError('メールアドレスまたはパスワードが正しくありません')
            #後でviewsから取り出すためフォームに保存
            self.user = user
        return cleaned_data
    
    #clean()の中でself.userに保存したユーザーを安全に取り出すための関数
    def get_user(self):
        return getattr(self, 'user', None)
    
#ユーザー名変更フォーム
class ChangeUsernameForm(forms.ModelForm):
    name = forms.CharField(
        label="新しいユーザー名",
        widget=forms.TextInput(attrs={'placeholder': '新しいユーザー名(20文字以下)'}),
    )
    class Meta:
        model = User #このフォームが操作するモデル
        fields = ['name'] #変更できる項目はnameだけ
        
    def clean_name(self):
        name = self.cleaned_data.get('name') #ユーザーが入力したnameの値をnameという変数に入れる
        if not name:  #nameが空やNoneの時
            raise forms.ValidationError('ユーザー名を入力してください')
        if not (1 <= len(name) <= 20):
            raise forms.ValidationError('ユーザー名は２０文字以下で入力してください')
        if self.instance and name == self.instance.name: #現在のユーザー名と新しいユーザー名が同じ時
            raise forms.ValidationError('現在のユーザー名と同じです')
        #nameの重複チェック(アカウント設定じとは内容異なる)
        qs = User.objects.filter(name=name) #qs=Querysetの略　Userテーブルからnameが一致するユーザーを全体取り出す
        if self.instance.pk: #自分自身は重複チェックから除外　self.instance.pk＝編集しているユーザー自身のID
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('このユーザー名は既に使われています')
        return name
    
#メールアドレス変更フォーム
class ChangeEmailForm(forms.ModelForm):
    email = forms.EmailField(
        label="新しいメールアドレス",
        widget=forms.EmailInput(attrs={'placeholder': 'xxx@example.com'})
    )
    class Meta:
        model = User
        fields = ['email']
        
    def clean_email(self):
        email = self.changed_data.get('email')
        if self.instance and email == self.instance.email: #現在のメールアドレスと新しいメールアドレスが同じ時
            raise forms.ValidationError('現在のメールアドレスと同じです')
        qs = User.objects.filter(email=email) #qs=Querysetの略　Userテーブルからemailが一致するユーザーを全体取り出す
        if self.instance.pk: #自分自身は重複チェックから除外　self.instance.pk＝編集しているユーザー自身のID
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('このメールアドレスは既に使われています')
        return email