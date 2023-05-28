# Создание архивов (OSTree archive)

Для распространения обновлений отведен отдельный OSTree-репозиторий в режиме [archive](https://ostree.readthedocs.io/en/stable/manual/formats).

# Пример на основе [подветки lighttpd](create_substream.md)
Обновите `lighttpd`, и соберите образ на базе первого коммита.

Добавьте в `archive`-репозиторий последний коммит: 
```shell
./pull-archive \
    altcos/x86_64/Sisyphus/lighttpd \
    a0a930bc978c2aaf4b86cd70ba8bb6c4fccf661e831a34b21e87be0a8b9a3c28
```

Запустите виртуалку с созданным образом.

При запуске демон [zincati](https://coreos.github.io/zincati) скачает обновления.

Вы можете его отключить:
```shell
systemctl disable --now zincati
```

В этом случае вам придется обновляться вручную:
```shell
ostree admin upgrade
```

---
После обновления необходимо выполнить перезагрузку:
```shell
reboot
```
