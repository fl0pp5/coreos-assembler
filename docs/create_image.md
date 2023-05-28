# Создание образов

Для создания образов используется `yaml`-конфиг, обрабатываемый скриптом `buildfile`.

# Пример
```yaml
# build.yml
altcos/x86_64/sisyphus:
  repo: bare
  commit: latest
  build:
    qemu:
      qcow2:
        sign: true
        archive: false

altcos/x86_64/p10:
  repo: archive
  commit: latest
  build:
    qemu:
      qcow2:
```

Запустим обработчик конфига
```shell
./buildfile build.yml private_altcos.pem
```
