‼️ Останнє оновлення - 9.03, 14-20
https://gitlab.com/a_gonda/nowarddos.git

‼️Для оновлення до версії від 9.03: навіть якщо до того було включено автооновлення - зараз все ж треба буде поставити нову версію руцями. Сорі, працюємо, щоб такого надалі не траплялося.

Алгоритм оновлення зараз наступний:
1. зупитяємо контейнери
2. видаляємо усю папку (запускати з папки, где скрипт): cd .. && rm -rf nowarddos
3. далі - як в інструкції: git clone https://gitlab.com/a_gonda/nowarddos.git && \
   cd nowarddos/ && \
   ./flood.sh run 3

🧨 Докер, розгортка на НОВОМУ інстансі в хмарі - TL;DR (перевірено на digital ocean):
git clone https://gitlab.com/a_gonda/nowarddos.git && \
cd nowarddos/ && \
./flood.sh run 3 <- запускає 3 контейнери з автоапдейтом та авторестартом

⚡️Новость от 08.03, 12-30 -> тестируем простой вариант исполнения в облаке. Детали тут: https://t.me/c/1617331726/13450

🤷‍♀️Для запуска локально: рекомендуется vpn, для облака - не обязательно. Можно запускать через докер (рекомендуемый способ: в облаке скорость как правильно может быть выше, и вы не будете нагружать каналы местного провайдера, которые могут быть нужны другим людям) или напрямую файл main.py -> без дополнительных параметров.

Также можно скачать готовые образы для докера: registry.gitlab.com/a_gonda/nowarddos:latest

Скрипт имеет свою команду запуска: flood.sh, которая принимает параметры.

Вывести все доступные команды для скрипта:
Находясь в папке со скриптом (в данном случае это /root/nowarddos):
./flood.sh . -> выводит

run {кількість контейнерів. Зараз - це рекомендована команда. Контейнери буде запущено, та вони будуть автоматично перевантажуватися та оновлятися. Приклад запуску: ./flood.sh run 3}
status
log
net
stop

1). run -> написано выше. Пример: ./flood.sh run 3
2). status -> выводит статус, сколько контейнеров запущено. Пример: ./flood.sh status
3). log -> выводит лог первого запущенного контейнера. Пример: ./flood.sh logs
4). net -> показывает текущий трафик через nload eth0. Пример ./flood.sh logs net
5). stop -> останавливает запущенные контейнеры. Пример ./flood.sh stop

Примечание: скорость  очень зависит от текущих таргетов, чем медленее сайты работают, тем скорость будет меньше. Чем больше их лежит - тем скорость тоже
может быть меньше