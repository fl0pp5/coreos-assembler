# Описание конфига buildfile

`buildfile` - это yaml-конфиг, обрабатываемый одноименным скриптом, для создания образов

- `Название потока (object)` - например `altcos/x86_64/sisyphus`
  - `repo (string)` - репозиторий на основе которого будет создан образ (`bare` или `archive`)
  - `commit (string)` - принимает хэш-сумму коммита или `latest`, указывая на последний коммит
  - `build (object)` - содержит платформы и форматы для сборки
    - `Название платформы (object)` - `qemu`, `metal`
      - `Название формата (object)` - `qcow2`, `iso`
        - `sign (bool)` - если `true` - подпишет образ
        - `archive (bool)` - если `true` - создаст `tar.gz` архив

# Запуск
```shell
./buildfile <название_конфига.yml> <ключ_подписи.pem>
```

# Примеры: [Тыц](create_image.md)
