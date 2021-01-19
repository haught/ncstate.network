#!/usr/bin/python

# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
module: tftp_send
author:
  - Matt Haught (@haught)
short_description: Send data directly to TFTP server from where ansible runs.
description:
  - This module allows sending files and text using TFTP.
  - The module sends from wherever the playbook is run.
options:
  host:
    description:
      - The IP address or hostname of destination TFTP server.
    required: True
    type: str
  port:
    description:
      - The port of destination TFTP server.
    required: False
    default: 69
    type: int
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
  blocksize:
    description:
      - TFTP transfer blocksize.
    required: False
    default: 512
    type: int
'''

EXAMPLES = """
tasks:
  - name: Send tftp file
    ncstate.network.tftp_send:
      host: 1.2.3.4
      src: {{ string }}
      dest_filename: '/dest/file.txt'
"""

RETURN = """
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

from tftpy import TftpClient
import io

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.basic import AnsibleModule

def main():
    spec = dict(
        host=dict(type='str', required=True),
        port=dict(default=69, type='int'),
        src=dict(type='str', required=True),
        dest_filename=dict(type='str', required=True),
        blocksize=dict(default=512, type='int')
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True
    )

    warnings = list()
    result = {'changed': False, 'warnings': warnings}
    responses = []

    if module.check_mode:
        warnings.append(
            'TFTP transfer cannot occur using check mode'
        )
        module.exit_json(**result)

    try:
        client = TftpClient(module.params['host'], module.params['port'], options={'blksize': module.params['blocksize']})
        responses.append('TFTP client connected to %s:%s' % (to_native(module.params['host']), to_native(module.params['port'])))
        try:
            client.upload(module.params['dest_filename'], io.StringIO(to_text(module.params['src'])))
            responses.append('TFTP client uploaded to %s' % to_native(module.params['dest_filename']))
            result['changed'] = False
        except Exception as err:
            module.fail_json(msg='TFTP upload failed: %s' % to_native(err), **result)
    except Exception as err:
        module.fail_json(msg='Client error occured: %s' % to_native(err), **result)

    result.update({
        'stdout': "\n".join(responses)
    })

    module.exit_json(**result)


if __name__ == '__main__':
    main()
