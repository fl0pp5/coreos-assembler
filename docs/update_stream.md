# Обновление потоков

Для обновления потоков используется конфиг `acosfile` c секцией `update: true`.

```yaml
# update_sisyphus.yml
altcos/x86_64/sisyphus:
  description: Minor sisyphus update
  version_part: minor
  update: true
  actions:
    - apt:
        update: true
        upgrade: true
```