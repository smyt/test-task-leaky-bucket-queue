# coding=utf-8
from twisted.internet import protocol, reactor, endpoints
from twisted.internet.defer import DeferredLock
from twisted.internet.task import LoopingCall


class ProcessorProtocol(protocol.Protocol):
    """
    Стандартный протокол, главное отличие в том,
    что при обработке входящих данных, они нтерпретируются как задача и отдаются на обработку обработчику
    """
    def __init__(self, _processor):
        self.processor = _processor

    def callback(self, message, task):
        self.transport.write(message)

    def dataReceived(self, data):
        self.processor.add_task(data, self.callback)


class ProcessorProtocolFactory(protocol.Factory):
    """
    Простая фабрика, которая проксирует обработчик processor в протокол
    """
    def __init__(self, _processor):
        self.processor = _processor

    def buildProtocol(self, addr):
        return ProcessorProtocol(self.processor)


class LeakyBucketProcessor(object):
    """
    Обработчик очереди задач по алгоритму https://en.wikipedia.org/wiki/Leaky_bucket

    Размер очереди определяется  параметром bandwidth при создании класса
    """

    def __init__(self, bandwidth=5):
        """

        :param bandwidth: максимальная длина очереди, по превышению которой запросы будут отсекаться
        """
        self.tasks = []
        self.bandwidth = bandwidth
        self._lock = DeferredLock()

    def do_next(self):
        """запуск очередной итерации, вызов идет блокирующий"""
        self._lock.run(self._do_next)

    def _do_next(self):
        # обработка задач в очереди
        if self.tasks:
            task = self.tasks.pop(0)
            # запускаем коллбэк в отдельном thread
            reactor.callInThread(task['callback'], message="task done: {}".format(task['data']), task=task)

    def add_task(self, data, callback):
        """
        добавление задачи в очередь, если есть место, вызов идет блокирующий

        :param data: данные для задачи
        :param callback: функция которая будет вызвана по завершению обработки задачи
        """
        return self._lock.run(self._add_task, {"data": data, "callback": callback})

    def _add_task(self, task):
        # добавление задачи в очередь
        # если нет переполнения очереди, то добавляем задачу
        if len(self.tasks) < self.bandwidth:
            self.tasks.append(task)
            # запускаем коллбэк в отдельном thread
            reactor.callInThread(task['callback'], message="task added: {}".format(task['data']), task=task)
        else:
            # запускаем коллбэк в отдельном thread
            reactor.callInThread(task['callback'], message="task refused: {}".format(task['data']), task=task)


if __name__ == '__main__':
    # создаем обработчик задач
    processor = LeakyBucketProcessor()

    # инициализируем цикл исполнения по таймеру
    loop = LoopingCall(processor.do_next)
    # запускаем с шагом в 2 секунды, собственно эмуляция падения капель из ведра
    loop.start(2)

    # запускаем сервер сообщений twisted, с фабрикой протокола, которой передали обработчик в качестве параметра
    factory = ProcessorProtocolFactory(processor)
    endpoints.serverFromString(reactor, "tcp:1234").listen(factory)
    reactor.run()
