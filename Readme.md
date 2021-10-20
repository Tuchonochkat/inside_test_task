# Get started
Чтобы собрать контейнер:
```shell
docker build -t inside .
```
Чтобы запустить контейнер:
```shell
docker run --name inside_api -d -p 8080:8080 inside
```

Чтобы запустить тесты:
```shell
docker exec -ti inside_api bash
python manage.py test
```

# Endpoints
`/api/registration/`\
Регистрация нового пользователя. Принимает POST запрос с телом вида:
```json
{
  "name": "user_name",
  "password": "user_password"
}
```

`/api/login/`\
Авторизация пользователя. Принимает POST запрос с телом вида:
```json
{
  "name": "user_name",
  "password": "user_password"
}
```
В случае удачной авторизации возвращает веб-токен JSON:
```json
{
  "token": "JWT"
}
```

`/api/message/`\
Отправка сообщения или запрос истории. Принимает запрос POST следующего вида с Bearer токеном в заголовке:
```json
{
  "name": "user_name",
  "message": "text"
}
```
В случае, если был отправлен запрос POST вида:
```json
{
  "name": "user_name",
  "message": "history N"
}
```
где N - любое неотрицательное целое число, возвращает последние N сообщений юзера.


`/api/delete_all_messages/`\
Принимает POST запрос с токеном в заголовке без тела. 
Удаляет все сообщения пользователя.