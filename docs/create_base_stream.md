# Создание базового потока

Инициализируем поток
```shell
./init-stream <branch> <arch>
# e.g. ./inti-stream sisyphus x86_64
```

Получим `rootfs`-образ, на базе которого будет создан поток
```shell
./get-rootfs <branch> <arch>
# e.g ./get-rootfs sisyphus x86_64
```

Приводим `rootfs` в вид `OSTree`-репозитория
```shell
sudo -E ./rootfs-to-repo <branch> <arch> <description>
# e.g. sudo -E ./rootfs-to-repo sisyphus x86_64 "initial commit"
# output:
# info: <commit>
```

Далее по теме:

[Создание образов](create_image.md)

[Создание подпотоков](create_substream.md)

[Создание OSTree-архивов](create_archive.md)