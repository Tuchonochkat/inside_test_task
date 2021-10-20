import jwt
from rest_framework import status, authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message
from .renderers import UserJSONRenderer
from .serializers import LoginSerializer, MessageSerializer, RegistrationSerializer


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data.get('message')
        # проверяем, не запрашивают ли историю
        if message.startswith('history'):
            split_message = message.split(' ')
            # в запросе только слово history и число
            if len(split_message) == 2:
                # если в запросе не число, возвращаем ошибку
                try:
                    m = int(split_message[1])
                    if m > 0:
                        all_messages = Message.objects.filter(name=serializer.validated_data.get('name'))\
                            .order_by('id').values_list('message', flat=True)
                        messages_to_show = {}
                        for i in range(0, min(m, len(all_messages))):
                            messages_to_show[len(all_messages)-i] = all_messages[len(all_messages)-i-1]
                        return Response(messages_to_show)
                    elif m == 0:
                        return Response({})
                    else:
                        return Response({'error': 'Нельзя вывести отрицательное число сообщений!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Введите количество сообщений цифрами'},
                                    status=status.HTTP_400_BAD_REQUEST)
        # если в запросе не history <>, сохраняем сообщение
        else:
            serializer.save()
            return Response(serializer.data["message"], status=status.HTTP_201_CREATED)


# удалить все сообщения пользователя
class DeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        token = authentication.get_authorization_header(request).split()[1].decode('utf-8')
        name = jwt.decode(token, options={"verify_signature": False})['name']
        Message.objects.filter(name=name).delete()
        return Response({'user': name,
                        'response': 'Все сообщения удалены'})