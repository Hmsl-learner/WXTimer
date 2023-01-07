from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

class UserData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        print('getData', request.user.profile.items)

        return Response({'code': 'get ok', 'items': request.user.profile.items})

    def post(self, request, format=None):
        user = request.user
        user.profile.items = request.data
        user.save()
        print('post data ', user.profile.items)
        return Response({'code': 'post ok'})

class WeixinLogin(APIView):
    def post(self, request, format=None):
        code = json.loads(request.body).get('code')
        appid = 'wx8be2b297530fcd66'
        appsecret='cafb02ac616686f8c205fdd3b328d6a3'
        # 微信接口服务地址
        base_url = 'https://api.weixin.qq.com/sns/jscode2session'
        # 微信接口服务的带参数的地址
        url = base_url + "?appid=" + appid + "&secret=" + appsecret + "&js_code=" + code + "&grant_type=authorization_code"
        response = requests.get(url)

        # print(response.json())
        # 处理获取的 openid
        try:
            openid = response.json()['openid']
            session_key = response.json()['session_key']
        except KeyError:
            print("keyError")
            return Response({'code': 'fail'})
        else:
            # 打印到后端命令行
            print(openid, session_key)
            try:
                user = User.objects.get(username=openid)
            except User.DoesNotExist:
                user = None

            if not user:
                user = User.objects.create(
                    username=openid,
                    password=openid
                )
            refresh = RefreshToken.for_user(user)

            return Response({
                'code': 'success',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
