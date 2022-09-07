#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: sftp_send
author:
  - Matt Haught (@haught)

short_description: Send data directly to SFTP server from where ansible runs.

description:
  - This module allows sending files and text using SFTP.
  - The module sends from wherever the playbook is run.

requirements:
  - python pysftp (pysftp)

options:
  host:
    description:
    - The IP address or hostname of destination SFTP server.
    required: True
    type: str
  port:
    description:
    - The port of destination SFTP server.
    required: False
    default: 22
    type: int
  username:
    description:
    - The username for the connection.
    required: True
    type: str
  password:
    description:
    - The password for the connection.
    required: True
    type: str
  src:
    description:
    - The text of the source file.
    required: True
    type: str
  dest_filename:
    description:
    - The destination filename.
    required: True
    type: str
'''

EXAMPLES = r"""
- name: Send sftp file
  ncstate.network.sftp_send:
      host: 1.2.3.4
      username: foo
      password: bar
      src: "{{ string }}"
      dest_filename: '/dest/file.txt'
"""

RETURN = r"""
stdout:
    description: The set of responses from the commands
    returned: always apart from low level errors (such as action plugin)
    type: list
    sample: ['...', '...']
stdout_lines:
    description: The value of stdout split into a list
    returned: always
    type: list
    sample: [['...', '...'], ['...'], ['...']]
"""

try:
    import pysftp
    HAS_PYSFTP = True
except ImportError:
    HAS_PYSFTP = False

from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def main():

    spec = dict(
        host=dict(type='str', required=True),
        port=dict(default=22, type='int'),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        src=dict(type='str', required=True),
        dest_filename=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True
    )

    if not HAS_PYSFTP:
        module.fail_json(
            msg=missing_required_lib("pysftp"),
        )

    warnings = list()
    result = {'changed': False, 'warnings': warnings}
    responses = []

    if module.check_mode:
        warnings.append(
            'SFTP transfer cannot occur using check mode'
        )
        module.exit_json(**result)

    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(
                host=module.params['host'],
                username=module.params['username'],
                password=module.params['password'],
                port=module.params['port'],
                cnopts=cnopts
        ) as sftp:
            try:
                f = sftp.open(module.params['dest_filename'], 'wb')
                f.write(to_text(module.params['src']))
                f.close()
                sftp.close()
                responses.append('SFTP client uploaded to %s' % to_native(module.params['dest_filename']))
            except Exception as err:
                module.fail_json(msg='SFTP upload failed: %s' % to_native(err), **result)
    except Exception as err:
        module.fail_json(msg='Client error occured: %s' % to_native(err), **result)

    result.update({
        'stdout': "\n".join(responses)
    })

    module.exit_json(**result)


if __name__ == '__main__':
    main()
