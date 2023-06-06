# Распространение ALTCOS

Для распространения образов/обновлений и информации о ветках используются скрипты
* `v1_graph.py` - сервер обновлений
* `repomd` - сборщих метаифнормации о ветке
* `reposum` - сборщих информации о доступных образах


# Пример

#### repomd

* Вывод информации в консоль
```shell
./repomd \
    altcos/x86_64/sisyphus \
    96a1670bc0902c1e679e8f59ccf05fe49b90a9af65a2e9a4eb59aadb71706f2a \
    --indent 4
```
* Запись данных в директорию коммита
```shell
# Нужен запуск от root'а
sudo -E ./repomd \
    altcos/x86_64/sisyphus \
    96a1670bc0902c1e679e8f59ccf05fe49b90a9af65a2e9a4eb59aadb71706f2a \
    --indent 4 \
    --write
```
В директории коммита появится файл `metadata.json`.

#### reposum
```shell
./reposum sisyphus > "$STREAMS_ROOT"/sisyphus.json
```


#### v1_graph.py
```shell
sudo -E ./v1_graph.py "$ALTCOS_BASE_URL" 80
```

При запуске образа, [zincati](https://coreos.github.io/zincati/) обратится к заданному адресу и скачает обновления.

