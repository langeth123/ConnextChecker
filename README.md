# ConnextChecker
### How to start checker
В файлик secrets.txt загружаем чисто приватники ЛИБО грузим данные из encoded_secrets (для пользователей AUTOSOFT)
Если все же загрузили шифрованные приватники, то укажите настройки SECRETS_TYPE = "AUTOSOFT" (для пользователей AUTOSOFT, если вставляете просто приватники, то любое другое значение пишите)
DECRYPT_TYPE - Для юзеров AUTOSOFT (остальным не нужно)
DISK - Для юзеров AUTOSOFT (остальным не нужно)

В proxies можно вставить прокси в формате:
~~~python

 proxies = [
        {
            "http": "http://user:pass@ip:port",
            "https": "http://user:pass@ip:port"
        }, 
        {
            "http": "http://user2:pass@ip:port",
            "https": "http://user2:pass@ip:port"
        }, 
        {
            "http": "http://user3:pass@ip:port",
            "https": "http://user3:pass@ip:port"
        } # optinal
    ]

~~~
Но и без прокси все прекрасно пашет
В целом все, запускаем py main.py и смотрим результаты в results.txt


### How to run script
1. Устанавливаем Python: https://www.python.org/downloads/, я использую версию 3.9.8
2. При установке ставим галочку на PATH при установке
3. Устанавливаем C++ модули из: https://visualstudio.microsoft.com/ru/visual-cpp-build-tools/

>![ScreenShot](https://img2.teletype.in/files/19/03/19032fbe-1912-4bf4-aed6-0f304c9bf12e.png)

3. После установки скачиваем бота, переносим все файлы в одну папку (создаете сами, в названии и пути к папке не должно быть кириллицы и пробелов)
4. Запускаем консоль (win+r -> cmd)
5. Пишем в консоль:
cd /d Директория
* Директория - путь к папке, где лежит скрипт (само название скрипта писать не нужно)
6. Прописываем:
pip install -r requirements.txt
