Web-приложение для системы опросов пользователей... Docker, Django, DRF, sqlite3.
=====
**Установка:**

Для запуска вам понадобиться docker-compose.

Запустить:

docker-compose up -d

**Типы вопросов:**

У "questions" есть "type":

"TX" - ответ текстом,
"1C" - ответ с выбором одного варианта,
"MC" - ответ с выбором нескольких вариантов.


**Описание АПИ администратора:**

Регистрация не нужна по ТЗ, добавлен админ с паролем и логином: admin

http://127.0.0.1:8000/admin_api/polls/

- Получение всех опросов и создание опроса( со всем содержимым).

Пример создания опроса:
```json
{
    "name": "Poll_1",
    "start_date": null,
    "end_date": null,
    "description": "Poll 1",
    "questions": [{
        "choices": [{"choice_text": "choice1_question_1"}, {"choice_text": "choice2_question_1"}, {"choice_text": "choice3_question_1"}],
        "type": "1C",
        "question_text": "Question_1_poll_1"
    },
    {
        "choices": [{"choice_text": "choice1_question_2"}, {"choice_text": "choice2_question_2"}, {"choice_text": "choice3_question_2"}],
        "type": "MC",
        "question_text": "Question_2_poll_1"
    },
    {
        "choices": [{"choice_text": null}],
        "type": "TX",
        "question_text": "Question_3_poll_1"
    }]
}
```

http://127.0.0.1:8000/admin_api/polls/1/

- Удаление и редактирование опроса. При редактировании существующие вопросы не редактирутся( - это ниже), и все предоставленные вопросы будут добавлены к опросу как новые.

Пример редактирования опроса:
```json
{
    "questions": [
        {
            "choices": [
                {
                    "choice_text": null
                }
            ],
            "type": "TX",
            "question_text": "ADD_Question_4_poll_1"
        }
    ],
    "name": "Poll_1",
    "end_date": "2020-06-30",
    "description": "Changed Poll 1"
}
```

http://127.0.0.1:8000/admin_api/questions/1/
- Редактирование, удаление вопроса. При редактировании существующие варианты ответов не редактирутся( - это ниже), и все предоставленные варианты будут добавлены к вопросу как новые.

- Пример редактирования вопроса:
```json
{
    "choices": [
        {
            "choice_text": "ADD choice4_question_1"
        }
    ],
    "type": "MC",
    "question_text": "Changed Question_1_poll_1"
}
```

http://127.0.0.1:8000/admin_api/choices/1/
- Редактирование, удаление варианта ответа:
- Пример:
```json
{
    "choice_text": "Changed choice1_question_1"
}
```

- Чтобы опрос стал активным добавим start_date:
http://127.0.0.1:8000/admin_api/polls/1/
```json
{
    "name": "Poll_1",
    "start_date":"2020-06-07",
    "end_date": "2020-06-30",
    "description": "Changed Poll 1"
}
```



**Описание пользовательского АПИ:**

http://127.0.0.1:8000/active_polls/
- Получение списка активных опросов

http://127.0.0.1:8000/user_poll_create/
- Ответить на вопросы опроса. Необходимо указать poll_id опроса, person_id отвечающего и его варианты ответов в choices( в поле choice будет id выбранного варианта ответа).
- Пример ответов:
```json
{
        "poll_id": 1,
        "person_id": 1,
        "choices": [
        {
            "answer_text": null,
            "choice": 2
        },
        {
            "answer_text": null,
            "choice": 4
        },
        {
            "answer_text": null,
            "choice": 6
        },
        {
            "answer_text": "Text answer 1",
            "choice": 7
        },
        {
            "answer_text": "Text answer 2",
            "choice": 8
        }
        ]
}
```

http://127.0.0.1:8000/user_polls/1/
- Получение пройденных пользователем опросов( 1 - ID пользователя)

http://127.0.0.1:8000/user_poll_detail/1/
- детализация по ответам опроса( 1 - номер пользовательского опроса из /user_polls выше). 
