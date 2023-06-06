# ALT CoreOS Assembler

Инструменты для создания, сопровождения и распространения `ALT CoreOS (altcos)`


# Подготовка
Для создания базовых веток нужен первоначальный `rootfs`-образ, он изготавливается при помощи [mkimage-profiles](https://www.altlinux.org/Mkimage-profiles).
```shell
git clone git://git.altlinux.org/gears/m/mkimage-profiles.git
```

Настроим переменные окружения
```shell
export STREAMS_ROOT="Хранилище потоков"
export MKIMAGE_PROFILES_ROOT="Путь до mkimage-profiles"
export BUILDS_ROOT="Хранилище образов"
export ALTCOS_BASE_URL="Адрес откуда будут скачиваться обновления"
```

Сгенерируем ключ для подписи образов

```shell
openssl genrsa -out private_altcos.pem 2048
```

Качаем нужные python-пакеты
```shell
apt-get install python3-module-rpm

# --system-site-packages нужен для библиотеки "rpm-python", которой нет в PyPI
python3 -m venv venv --system-site-packages

pip install -r requirements.txt
```

# Начало работы

[Создание базового потока](docs/create_base_stream.md)

[Создание образов](docs/create_image.md)

[Создание подпотоков](docs/create_substream.md)

[Создание архивов](docs/create_archive.md)

[Распространение](docs/spread.md)