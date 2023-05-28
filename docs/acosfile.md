# Описание конфига acosfile

`buildfile` - это yaml-конфиг, обрабатываемый одноименным скриптом, для создания подпотоков и обновления потоков/подпотоков

- `Название потока (object)` - например `altcos/x86_64/P10/k8s`
    - `description (string)` - сообщение коммита
    - `version_part (string)` - часть версии, которую нужно увеличить на 1. Доступны только два значения `major,minor`. 
Если потока не существовала, версия не увеличивается.
    - `forward_root (string)` - директория, которая будет проброшена в `butane`
    - `update (bool)` - указывает на то, что происходит обновление ветки, а не создание
    - `apt (list of objects)` - секция для управления пакетами
      - `install (list of strings)` - список пакетов для установки
      - `remove (list of strings)` - список пакетов для удаления
      - `update (bool)` - флаг обновления репозитория
      - `upgrade (bool)` - флаг обновления системы
    - `run (string)` - команды, которые нужно запустить в chroot'е
    - `butane (object)` - конфиг [butane](https://coreos.github.io/butane)
    - `env (list of objects)` - переменные окружения заданные ввиде `<ключ>:<значение|cmd (см. ниже)>`
      - `cmd (string)` - выполнить команду и присвоить ее результат переменной окружения
    - `podman (object)` - образы для копирования (через [skopeo](https://github.com/containers/skopeo))
      - `env_list_images (string)` - переменные окружения содержщие адреса образов, перечисленные через запятую
      - `images (list of strings)` - адреса образов

# Запуск
```shell
./acosfile <название_конфига.yml>
```

# Примеры: [раз](create_substream.md), [два](update_stream.md)