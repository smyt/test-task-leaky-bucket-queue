**Времени затрачено:** 4. 5 часа

Задача #1
=========

Что вернет функция call_foo вызванная с парaметром A(5)?
```
class A(object):
    def __init__(self, value):
        self._value = value

    def foo(self):
        self.bar()
        return self._value

def call_foo(inst):
    try:
        assert isinstance(inst, A)
        if inst.foo() < 10:
            return True
        else:
            return False
    except AttributeError:
        return False
    finally:
        return False
```

**Ответ:** Вернет False

Задача #2
=========

Исправьте код из задания 1. не изменяя класс A и функцию call_foo, так, чтобы
AttributeError не возникал.

Что вернет функция call_foo если параметр переданный в A.__init__ будет снова равен 5?

Почему?

**Ответ:** снова вернет False, хотя inst.foo() и меньше 10 (а меньше 10 оно потому что функция foo возвращает значение self._value, а self._value инициализируется 5 при вызове конструктора класса A со значением 5) но вызов блока finally обязателен согласно пункту 8.6 https://docs.python.org/2/tutorial/errors.html: The finally clause is also executed “on the way out” when any other clause of the try statement is left via a break, continue or return statement.

вариант исправления:

```
class A(object):
    def __init__(self, value):
        self._value = value

    def foo(self):
        # тут убрал строчку
        return self._value

def call_foo(inst):
    try:
        assert isinstance(inst, A)
        if inst.foo() < 10:
            return True
        else:
            return False
    except AttributeError:
        return False
    finally:
        return False
```

Задача #3
=========

Реализуйте алгоритм [https://en.wikipedia.org/wiki/Leaky_bucket](https://en.wikipedia.org/wiki/Leaky_bucket) для ограничения сетевой скорости приложения. Реализованный алгоритм должен быть потокобезопасным и использовать минимум ресурсов системы

Получился простой twisted-based сервер, который для эмуляции сетевой активности пропускает через себя входящие tcp сообщения.

Зависимости
-----------

* python 2.7

Установка
---------

```
pip install -r requirements.txt
```

Запуск
------

```
python app.py
```

Как работает
------------

Создан класс обработчик Processor, которые отвечает за обработку запросов по алгоритму Leaky bucket. Выбрана вариация на основе очереди.

При запуске сервера запускается LoopingCall, который с шагов в 2 секунды стреляет обработку задачи через do_next, для потокобезопасности используется DeferredLock, который блокирует изменение списка задачи на время выполнения.

Чтобы проверить работу сервера, надо его запустить:

```
python app.py
```

подключится по tcp, к порту 1234:

```
netcat localhost 1234
```

Чего-нибудь попосылать, каждое сообщение воспринимается как данные для одной задачи, по умолчанию стоит ограничение ведра в 5 задач. По привышении размера очереди, будет приходить сообщение *task refused*

Пример общения:

```
1
task added: 1
2
task added: 2
3
task added: 3
4
task added: 4
5
task added: 5
task done: 1
1
task added: 1
2
task refused: 2
3123
task refused: 3123
```


