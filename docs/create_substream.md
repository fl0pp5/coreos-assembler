# Создание подпотоков 

Для примера создадим подпоток на основе ветки `altcos/x86_64/sisyphus`.

* Создадим yml-конфиг
```yaml
# lighttpd.yml
altcos/x86_64/Sisyphus/lighttpd:
  description: Initial commit for lighttpd stream
  actions:
    - apt:
        update: true
        upgrade: true
        install:
          - htop
          - lighttpd
    - butane:
        variant: fcos
        version: 1.3.0
        systemd:
          units:
              - name: lighttpd.service
                enabled: true
```
* Запускаем скрипт для обработки конфига
```shell
./acosfile lighttpd.yml
```

# Дополнительно
Вы можете создать несколько подветок за раз, например

```yaml
# few_streams.yml
altcos/x86_64/Sisyphus/first:
  description: First
  actions:
    - apt:
        update: true
        upgrade: true
        install:
          - htop
          - lighttpd
    - butane:
        variant: fcos
        version: 1.3.0
        systemd:
          units:
            - name: lighttpd.service
              enabled: true

altcos/x86_64/Sisyphus/second:
  description: Second
  actions:
    - run:
        - |
          touch mysuperfile.txt
```

***
[Документания по написанию конфига](acosfile.md)
