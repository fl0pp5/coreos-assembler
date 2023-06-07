# Распространение ALTCOS

Для распространения образов/обновлений и информации о ветках используются скрипты
* `v1_graph.py` - сервер обновлений
* `refsum` - сборщих метаифнормации о ветке
* `buildsum` - сборщих информации о доступных образах


# Пример

#### refsum

* Вывод информации в консоль
```shell
./refsum \
    altcos/x86_64/sisyphus \
    96a1670bc0902c1e679e8f59ccf05fe49b90a9af65a2e9a4eb59aadb71706f2a \
    --indent 4
```
* Запись данных в директорию коммита
```shell
# Нужен запуск от root'а
sudo -E ./refsum \
    altcos/x86_64/sisyphus \
    96a1670bc0902c1e679e8f59ccf05fe49b90a9af65a2e9a4eb59aadb71706f2a \
    --indent 4 \
    --write
```
В директории коммита появится файл `metadata.json`.

#### buildsum
```shell
./buildsum sisyphus > "$STREAMS_ROOT"/sisyphus.json
```


#### v1_graph.py
```shell
sudo -E ./v1_graph.py "$ALTCOS_BASE_URL" 80
```

При запуске образа, [zincati](https://coreos.github.io/zincati/) обратится к заданному адресу и скачает обновления.

