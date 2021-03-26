#!/usr/bin/python
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: apc_snmpv3
author: "Matt Haught (@haught)"
short_description: Manage snmpv3 configuration on APC devices.
description:
  - This module provides declarative management of APC snmpv3
    on APC UPS NMC systems.
notes:
  - Tested APC NMC v3 (AP9641) running APC OS v1.4.2.1
options:
  enable:
    description:
      - Global SNMPv3 enable.
    type: bool
  index:
    description:
      - Index of SNMPv3 user.
    type: str
  username:
    description:
      - SNMPv3 user name for index.
    type: str
  authprotocol:
    description:
      - SNMPv3 authentication protocol for index.
    type: str
  authphrase:
    description:
      - SNMPv3 authentication phrase for index.
    type: str
  privprotocol:
    description:
      - SNMPv3 privacy protocol for index.
    type: str
  privphrase:
    description:
      - SNMPv3 privacy phrase for index.
    type: str
  access:
    description:
      - SNMPv3 access enable for index.
    type: bool
  accessusername:
    description:
      - SNMPv3 access user name for index.
    type: str
  accessaddress:
    description:
      - SNMPv3 NMS IP/CIDR address for index.
  forcepwchange:
    description:
      - Force a auth/priv phrase change
    type: bool
'''

EXAMPLES = """
- name: Set snmpv3 name
  ncstate.network.apc_snmpv3:
    primarysnmpv3: "1.1.1.1"

- name: Set two snmpv3 settings
  ncstate.network.apc_snmpv3:
    primarysnmpv3: "1.1.1.1"
    secondarysnmpv3: "4.4.4.4"
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - snmpv3 -n ups001
"""
import re
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import CustomNetworkConfig
from ansible_collections.ncstate.network.plugins.module_utils.network.apc import (
    load_config,
    get_config,
    parse_config,
    parse_config_section,
)

SOURCE = "snmpv3"

def build_commands(module):
    commands = []
    config = {}
    config['config'] = parse_config_section(get_config(module, source=SOURCE), 'SNMPv3 Configuration')
    config['user'] = parse_config_section(get_config(module, source=SOURCE), 'SNMPv3 User Profiles', module.params['index'])
    config['access'] = parse_config_section(get_config(module, source=SOURCE), 'SNMPv3 Access Control', module.params['index'])
    if module.params['enable']:
        if config['config']['snmpv3'] == "disabled" and module.params['enable'] == True:
            commands.append(SOURCE + ' -S enable')
        elif config['config']['snmpv3'] == "enabled" and module.params['enable'] == False:
            commands.append(SOURCE + ' -S disable')
    if module.params['authprotocol'] and module.params['index']:
        if config['user']['authentication'] != module.params['authprotocol']:
            commands.append(SOURCE + ' -ap' + str(module.params['index']) + ' '  + module.params['authprotocol'])
    if module.params['privprotocol'] and module.params['index']:
        if config['user']['encryption'] != module.params['privprotocol']:
            commands.append(SOURCE + ' -pp' + str(module.params['index']) + ' '  + module.params['privprotocol'])
    if module.params['username'] and module.params['index']:
        if config['user']['username'] != module.params['username']:
            commands.append(SOURCE + ' -u' + str(module.params['index']) + ' '  + module.params['username'])
        # set password if username changes or set to force
        if (module.params['username'] and config['user']['username'] != module.params['username']) or module.params['forcepwchange'] == True:
            if module.params['authphrase'] and module.params['index']:
                commands.append(SOURCE + ' -a' + str(module.params['index']) + ' '  + module.params['authphrase'])
            if module.params['privphrase'] and module.params['index']:
                commands.append(SOURCE + ' -c' + str(module.params['index']) + ' '  + module.params['privphrase'])
    if module.params['accessusername'] and module.params['index']:
        if config['access']['username'] != module.params['accessusername']:
            commands.append(SOURCE + ' -au' + str(module.params['index']) + ' '  + module.params['accessusername'])
    if module.params['access'] and module.params['index']:
        if config['access']['access'] == "disabled" and module.params['access'] == True:
            commands.append(SOURCE + ' -ac' + str(module.params['index']) + ' enable')
        elif config['access']['access'] == "enabled" and module.params['access'] == False:
            commands.append(SOURCE + ' -ac' + str(module.params['index']) + ' disable')
    if module.params['accessaddress'] and module.params['index']:
        if config['access']['nmsip/hostname'] != module.params['accessaddress']:
            commands.append(SOURCE + ' -n' + str(module.params['index']) + ' '  + module.params['accessaddress'])
    return commands

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        enable=dict(type='bool'),
        index=dict(type='int', choices=[1, 2, 3, 4]),
        username =dict(type='str'),
        authphrase=dict(type='str'),
        authprotocol=dict(type='str', choices=['SHA', 'MD5', 'NONE']),
        privphrase=dict(type='str'),
        privprotocol=dict(type='str', choices=['AES', 'DES', 'NONE']),
        access=dict(type='bool'),
        accessusername=dict(type='str'),
        accessaddress=dict(type='str'),
        forcepwchange=dict(type='bool', default=False)
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           required_by={
                             'username': 'index',
                             'authphrase': 'index',
                             'authprotocol': 'index',
                             'privphrase': 'index',
                             'privprotocol': 'index',
                             'access': 'index',
                             'accessusername': 'index',
                             'accessaddress': 'index',
                             'forcepwchange': 'index',
                           },
                           supports_check_mode=True)

    warnings = list()

    result = {'changed': False}

    if warnings:
        result['warnings'] = warnings

    commands = []
    commands = build_commands(module)

    result['commands'] = commands

    if commands:
        if not module.check_mode:
            load_config(module, commands)

        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
