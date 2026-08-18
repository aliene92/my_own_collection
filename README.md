# Домашнее задание к занятию 6 «Создание собственных модулей»

## Подготовка окружения
Настройка тестового окружения показана на скриншоте ниже.
![scr1](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/testenv.png)
Проверка версий:

```bash
ansible --version
ansible-galaxy --version
python3 --version
pip3 --version
git --version
```

Используемые версии:

```text
ansible-core 2.22.0
Python 3.14.4
pip 25.1.1
git 2.53.0
```
![scr2](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/vers.png)

## Инициализация Ansible collection

Collection была создана командой:

```bash
ansible-galaxy collection init my_own_namespace.yandex_cloud_elk
```

После этого collection была размещена в стандартной структуре Ansible collections:

```text
ansible/my_own_namespace/yandex_cloud_elk
```

Итоговый путь collection:

```text
/home/mrk/ansible/4p/ansible/my_own_namespace/yandex_cloud_elk
```

---
## Создание собственного Ansible module

Модуль был создан в каталоге:

```text
ansible/my_own_namespace/yandex_cloud_elk/plugins/modules/my_own_module.py
```

Модуль принимает два обязательных параметра:

| Параметр | Тип | Обязательный | Описание |
|---|---|---|---|
| `path` | string | да | Путь к создаваемому или обновляемому файлу |
| `content` | string | да | Содержимое файла |

Логика работы модуля:

1. Получает параметры `path` и `content`.
2. Проверяет, существует ли файл по указанному пути.
3. Если файл существует и его содержимое уже совпадает с нужным, возвращает `changed: false`.
4. Если файла нет или его содержимое отличается, создаёт или обновляет файл.
5. Возвращает `changed: true`, если файл был создан или изменён.
6. Поддерживает `check_mode`.

---

## Содержимое custom module

Файл:

```text
ansible/my_own_namespace/yandex_cloud_elk/plugins/modules/my_own_module.py
```

Основная логика модуля:

```python
#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        path='',
        content='',
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    path = module.params['path']
    content = module.params['content']

    result['path'] = path
    result['content'] = content

    current_content = None

    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                current_content = file.read()
        except Exception as error:
            module.fail_json(
                msg='Failed to read existing file: {0}'.format(error),
                **result
            )

    if current_content == content:
        result['changed'] = False
        result['message'] = 'File already exists with required content'
        module.exit_json(**result)

    result['changed'] = True

    if module.check_mode:
        result['message'] = 'File would be created or updated'
        module.exit_json(**result)

    directory = os.path.dirname(path)

    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as error:
            module.fail_json(
                msg='Failed to create directory: {0}'.format(error),
                **result
            )

    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as error:
        module.fail_json(
            msg='Failed to write file: {0}'.format(error),
            **result
        )

    result['message'] = 'File has been created or updated'
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
```

---

## Локальная проверка module

Проверка выполнялась прямым запуском Python-файла модуля.

Команда:

```bash
python3 plugins/modules/my_own_module.py <<'EOF'
{"ANSIBLE_MODULE_ARGS": {"path": "/tmp/my_own_module_local_test.txt", "content": "Hello from local module test"}}
EOF
```
Команда выполнена два раза, при первом запуске был создан файл, при втором не было выполнено никаких изменений. Скриншот ниже
![scr3](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/resmod.png)

## Single task playbook для проверки module

Для проверки модуля через Ansible был создан playbook:

```text
test_module.yml
```

Содержимое файла:

```yaml
---
- name: Test custom Ansible module
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create file using my own module
      my_own_namespace.yandex_cloud_elk.my_own_module:
        path: /tmp/my_own_module_playbook_test.txt
        content: "Hello from custom Ansible module"
```

Запуск playbook:

```bash
ANSIBLE_COLLECTIONS_PATH=/home/mrk/.ansible/collections/ansible_collections ansible-playbook test_module.yml
```
Playbook выполнен два раза, при первом запуске был создан файл, при втором не было выполнено никаких изменений. Скриншот ниже
![scr4](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/resspb.png)

## Создание role внутри collection

Single task playbook был преобразован в single task role внутри collection.

Role создана в каталоге:

```text
ansible/my_own_namespace/yandex_cloud_elk/roles/create_file
```

Структура role:

```text
roles/create_file/
├── defaults
│   └── main.yml
└── tasks
    └── main.yml
```

---

## Default-переменные role

Файл:

```text
ansible/my_own_namespace/yandex_cloud_elk/roles/create_file/defaults/main.yml
```

Содержимое:

```yaml
---
my_own_module_path: /tmp/my_own_module_role_test.txt
my_own_module_content: "Hello from custom Ansible role"
```

---

## Tasks role

Файл:

```text
ansible/my_own_namespace/yandex_cloud_elk/roles/create_file/tasks/main.yml
```

Содержимое:

```yaml
---
- name: Create file using my own module
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: "{{ my_own_module_path }}"
    content: "{{ my_own_module_content }}"
```

---

## Playbook для проверки role

Для проверки role был создан playbook:

```text
test_role.yml
```

Содержимое:

```yaml
---
- name: Test custom role from collection
  hosts: localhost
  gather_facts: false

  roles:
    - role: my_own_namespace.yandex_cloud_elk.create_file
```

Запуск playbook:

```bash
ANSIBLE_COLLECTIONS_PATH=/home/mrk/.ansible/collections/ansible_collections ansible-playbook test_role.yml
```

Повторный запуск подтверждает идемпотентность. Ниже скриншот.
![scr5](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/resrol.png)

---
## Документация collection

В collection заполнены основные файлы документации и метаданных:

```text
ansible/my_own_namespace/yandex_cloud_elk/README.md
ansible/my_own_namespace/yandex_cloud_elk/galaxy.yml
```

Файл `galaxy.yml`:
```
---
namespace: my_own_namespace
name: yandex_cloud_elk
version: 1.0.0
readme: README.md
authors:
  - Alexey Markov
description: Custom Ansible collection with module and role for creating text files.
license:
  - MIT
tags:
  - ansible
  - module
  - collection
  - file
  - homework
dependencies: {}
repository: https://github.com/aliene92/my_own_collection
documentation: https://github.com/aliene92/my_own_collection
homepage: https://github.com/aliene92/my_own_collection
issues: https://github.com/aliene92/my_own_collection
build_ignore:
  - "*.tar.gz"
  - ".git"
  - ".gitignore"
```
---
## Сборка collection

Сборка collection выполнялась из корня collection:

```bash
ansible-galaxy collection build --force
```

Результат:

```text
Created collection for my_own_namespace.yandex_cloud_elk at /home/mrk/ansible/4p/ansible/my_own_namespace/yandex_cloud_elk/my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz

```

Проверка архива:

```bash
ls -lh *.tar.gz
```

Результат:

```text
-rw-rw-r-- 1 mrk mrk 5.2K Aug 19 01:32 my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz
```
![scr6](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/tar.png)

## Проверка установки collection из локального архива

Для проверки установки collection из локального архива была создана отдельная директория:

```text
install_test
```

В неё были помещены:

```text
install_test/
├── my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz
└── test_installed_collection.yml
```

---

## Playbook для проверки установленной collection

Файл:

```text
install_test/test_installed_collection.yml
```

Содержимое:

```yaml
---
- name: Test installed custom collection
  hosts: localhost
  gather_facts: false

  roles:
    - role: my_own_namespace.yandex_cloud_elk.create_file
      vars:
        my_own_module_path: /tmp/my_own_module_installed_collection_test.txt
        my_own_module_content: "Hello from installed custom collection"
```

---

## Установка collection из архива

Команда установки:

```bash
ansible-galaxy collection install my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz --force
```
## Запуск playbook с установленной collection

Первый запуск:

```bash
ansible-playbook test_installed_collection.yml
```
На скриншоте ниже видно успешную установку и запуск. при первом запуске создается файл, при повторном изменений не происходит.
![scr7](https://github.com/aliene92/netoLo/blob/main/ansible/modules/scrs/rescol.png)

## Фиксация результата в Git

После выполнения всех этапов изменения были добавлены в Git:

```bash
git add .
git commit -m "Add custom ansible module collection"
git tag 1.0.0

git push origin main
git push origin 1.0.0
```
