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
