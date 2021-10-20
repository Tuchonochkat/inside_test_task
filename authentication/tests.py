import json

from rest_framework import status
from rest_framework.test import APITestCase


class InsideTestCase(APITestCase):
    def setUp(self):
        # создать пользователя
        self.user = self.client.post('/api/registration/',
                                     json.dumps({'name': 'test_user', 'password': 'test_password'}),
                                     content_type='application/json')
        # получить веб-токен JSON для вновь созданного пользователя
        response = self.client.post('/api/login/',
                                    json.dumps({'name': 'test_user', 'password': 'test_password'}),
                                    content_type='application/json')
        self.token = response.data['token']
        self.api_authentication()

    # функция аутентификации
    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+self.token)

    # функция удаляет все сообщения и создаёт n новых
    def create_messages(self, n):
        self.client.delete('/api/delete_all_messages/')
        for i in range(n):
            self.client.post('/api/message/', data={'name': 'test_user', 'message': 'Lorem ipsum '+str(i)})

    # функция проверяет выдачу истории для запроса m при количестве сообщений n в базе
    def check_history(self, m, n):
        self.create_messages(n)
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'history '+str(m)})
        if type(m) == int and m >= 0:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # сколько сообщений должно быть выведено
            if n == 0 or m == 0:
                k = 0
            elif n in range(1, m):
                k = n
            else:
                k = m
            self.assertEqual(len(response.data), k)
            # должны быть выведены именно последние сообщения
            if k > 0:
                for i in range(1, k+1):
                    self.assertEqual(response.data[n-i+1], 'Lorem ipsum '+str(n-i))
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # создание сообщения, когда пользователь аутентифицирован и имя совпало с именем в токене
    def test_create_message_authenticated_right(self):
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'Lorem ipsum'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # создание сообщения, когда пользователь не аутентифицирован
    def test_create_message_not_authenticated(self):
        self.client.force_authenticate(token=None)
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'Lorem ipsum'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # создание сообщения, когда пользователь аутентифицирован и имя не совпало с именем в токене
    def test_create_message_authenticated_wrong(self):
        self.client.force_authenticate(token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                                             'eyJuYW1lIjoidXNlcjQifQ.q_GGP94NsEeoXNiZqsSdQ_DXrK7N6RKhbkKr-c7agug')
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'Lorem ipsum'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # создание слишком длинного сообщения (ограничение 1023)
    def test_create_long_message(self):
        message = 'Lorem ipsum'*103
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': message})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # проверяем, что сообщение не попало в базу
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'history 1'})
        self.assertNotContains(response, message, status_code=status.HTTP_200_OK)

    # удаление сообщений пользователя
    def test_delete_all_messages(self):
        response = self.client.delete('/api/delete_all_messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], 'Все сообщения удалены')
        # проверяем, что в истории не осталось сообщений
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'history 10'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # тестирование истории
    # серия тестов для запроса 'history 10'
    # запрос пустой истории
    def test_get_history_10_empty(self):
        self.check_history(10, 0)

    # запрос истории, где кол-во сообщений меньше 10
    def test_get_history_10_middle(self):
        self.check_history(10, 9)

    # запрос истории, где кол-во сообщений больше или равно 10
    def test_get_history_10_lot(self):
        self.check_history(10, 11)

    # тесты для запроса 'history 0'
    # запрос пустой истории
    def test_get_history_0_empty(self):
        self.check_history(0, 0)

    # запрос для не пустой истории
    def test_get_history_0_lot(self):
        self.check_history(0, 9)

    # тесты для запроса 'history 1000'
    # запрос пустой истории
    def test_get_history_1000_empty(self):
        self.check_history(1000, 0)

    # запрос истории, где кол-во сообщений меньше 1000
    def test_get_history_1000_middle(self):
        self.check_history(1000, 300)

    # запрос истории, где кол-во сообщений больше или равно 1000
    def test_get_history_1000_lot(self):
        self.check_history(1000, 1001)

    # тест для запроса 'history -5'
    def test_get_history_negative(self):
        self.check_history(-5, 10)

    # тест для запроса 'history йцукен'
    def test_get_history_string(self):
        self.check_history('йцукен', 10)

    # запрос истории, когда пользователь аутентифицирован и имя не совпало с именем в токене
    def test_get_history_authenticated_wrong(self):
        self.client.force_authenticate(token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                                             'eyJuYW1lIjoidXNlcjQifQ.q_GGP94NsEeoXNiZqsSdQ_DXrK7N6RKhbkKr-c7agug')
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'history 10'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # запрос истории, когда пользователь не аутентифицирован
    def test_get_history_not_authenticated(self):
        self.client.force_authenticate()
        response = self.client.post('/api/message/', data={'name': 'test_user', 'message': 'history 10'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
