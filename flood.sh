#!/bin/bash
status() {
  docker ps
}

stop() {
  docker-compose -f docker-compose.yml down
}

log() {
  docker logs -f -n 100 $(docker ps -lq)
}

net() {
  nload eth0
}

restart() {
  docker-compose -f docker-compose.yml down && \
  docker-compose -f docker-compose.yml up --build -d --scale attacker=$2
}

run() {
  countainter_count="$2"
  echo "Запускаємо скрипт на $countainter_count контейнерах у автоматичному режимі"
  crontab -r

  echo "Створюємо крон для перезапуску $countainter_count контейнерів"
  restart_croncmd="cd $(pwd) && sh flood.sh restart $countainter_count"
  restart_cronjob="0,10,20,40,50 * * * * $restart_croncmd"
  ( crontab -l | grep -v -F "$restart_croncmd" ; echo "$restart_cronjob" ) | crontab -

  echo "Створюємо крон для оновлення $countainter_count контейнерів"
  update_parent_dir=$(cd ../ && pwd)
  update_current_dir=$(pwd)
  update_croncmd="cd ${update_parent_dir} && sh update.sh ${update_current_dir} $countainter_count"
  update_cronjob="30 * * * * $update_croncmd"
  ( crontab -l | grep -v -F "$update_croncmd" ; echo "$update_cronjob" ) | crontab -

  sudo apt-get update && yes | apt install docker.io && \
  yes | apt install docker-compose && \
  docker-compose -f docker-compose.yml up --build -d --scale attacker=$countainter_count && \
  apt install nload && \
  cp update.sh .. && \
  echo ">>>

  Автоматизацію підключено. Скрипт буде перезавантажуватися кожні 10 хв, та оновлюватися - кожну годину. Якщо включено перегряд логів, то під час перезавантаження вони зникають, це нормально. Через деякий час після перезавантаження (до хвилини), логи будуть доступні знову.
  Подивитись логи: ./flood.sh log. Перелік інших команд: ./flood.sh ?

  Слава Україні! Ми переможемо!

  <<<"
}

case "$1" in
run)
  run "$@"; exit $?;;
status)
  status "$@"; exit $?;;
log)
  log "$@"; exit $?;;
net)
  net "$@"; exit $?;;
restart)
  restart "$@"; exit $?;;
stop)
  stop "$@"; exit $?;;
*)
  echo "Usage: $0
   run {кількість контейнерів. Зараз - це рекомендована команда. Контейнери буде запущено, та вони будуть автоматично перевантажуватися та оновлятися. Приклад запуску: ./flood.sh run 3}
   status
   log
   net
   stop";
   exit 1;
esac
exit 0