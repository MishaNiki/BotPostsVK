# BotPostsVK

Телеграмм бот, который выводит посты вконтакте открытых сообществ вконтакте.

__Теперь новости интересующих вас сообществ в вконтакте можно будет смотреть через телеграмм бота!__

![Меню сообществ](static/menu_community.png)

![Пример вывода поста](static/posts.png)

## Установка

Нужно создать Standalone-Приложение вконтакте, для доступа к API. После получить  access token по следующему url:

```
https://oauth.vk.com/authorize?client_id=&display=page&redirect_uri=&scope=wall,photos&response_type=token&v=5.52
```

Ввести полученный токен в config.py поле VK_TOKEN. В поле BOT_TOKEN ввести токен от вашего бота 