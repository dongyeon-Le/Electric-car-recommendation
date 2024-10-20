from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Users

class CustomLogin(BaseBackend):
    def authenticate(self, request, userid=None, password=None, **kwargs):
        try:
            # 사용자 ID로 사용자 조회
            user = Users.objects.get(userid=userid)
        except Users.DoesNotExist:
            return None

        # 비밀번호 검증
        if user and check_password(password, user.password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return None