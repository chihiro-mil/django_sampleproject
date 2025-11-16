#Djangoのモデルをインポート
from django.db import models
#AbstractBaseUser:パスワード、ログイン機能の土台　PermissionsMixin:権限を追加　BaseUserManager:create_user　create_superuserを作るための土台
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
#created_at updated_atの初期値に日時を入れる
from django.utils import timezone

#ユーザーを作成するための専用クラス
class UserManager(BaseUserManager):
    #一般ユーザー用のcreate_user()
    def create_user(self, email, name, password=None, **extra_fields):
        #システム内部からでも不正なデータが入らないように守るバリエーション（エラーメッセージはコンソールに表示される）
        if not email:
            raise ValueError('メールアドレスは必須です')
        if not name:
            raise ValueError('ユーザー名は必須です')
        
        #メールアドレスの形をきれいに整える処理　normalize_emailはBaseUserManagerに用意されているメゾット　余分なスペースの削除やドメイン部分を小文字にする
        email = self.normalize_email(email)
        
        #Userクラスのインスタンス（保存前のユーザー1人分のデータを作っている）　**extra_fieldsは他に追加したいフィールドがあればまとめてここに渡せるように
        user = self.model(
            email=email,
            name=name,
            **extra_fields,
        )
        #パスワードをハッシュ化してセット
        user.set_password(password)
        
        #一般ユーザーなので基本はスタッフ権限なし
        user.is_active = True
        user.is_staff = False
        
        user.save(using=self._db)
        return user
    #管理者ユーザー用のcreate_superuser()
    def create_superuser(self, email, name, password=None, **extra_fields):
        #まずは普通のユーザーとして作成してから後で管理者フラグをONにする
        user = self.create_user(
            email=email,
            name=name,
            password=password,
            **extra_fields,
        )
        #このユーザーはスタッフに入る
        user.is_staff = True
        #このユーザーは全権限を与えます
        user.is_superuser = True
        #変更した内容をDBに保存し直す
        user.save(using=self._db)
        return user


#ユーザーモデル
class User(AbstractBaseUser, PermissionsMixin):
    #Userモデルのカラム
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=20)
    #アカウント有効か BooleanField:真偽値のフィールド
    is_active = models.BooleanField(default=True)
    #管理サイトに入れるか
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    #User.objects で使うマネージャー
    objects = UserManager()
    #メールアドレスとパスワードでログインできるように
    USERNAME_FIELD = 'email'
    #スーパーユーザー作成時に追加で必須にする項目
    REQUIRED_FIELDS = ['name']
    
    #管理者画面やシェルで各ユーザーをどのように表示するか決める（今回はメールアドレスでユーザー一覧が表示される）
    def __str__(self):
        return self.email
