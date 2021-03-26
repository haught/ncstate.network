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
    on APC UPS systems.
notes:
  - Tested against Smart-UPS SRT 1500 with APC OS v6.8.2
options:
  enable:
    description:
      - Global SNMPv1 enable.
    type: bool
  index:
    description:
      - Index of SNMPv1 user.
    type: str
    choices: [1, 2, 3, 4]
  community:
    description:
      - SNMPv1 community name.
    type: str
  accesstype:
    description:
      - SNMPv3 access enable for index.
    type: bool
    choices: ['disabled', 'read', 'write', 'writeplus']
  accessaddress:
    description:
      - SNMPv1 NMS IP/CIDR address for index.
'''

EXAMPLES = """
- name: Set snmpv3 name
  ncstate.network.apc_snmp:
    index: 1
    community: "public"
    accesstype: "read"
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - snmp -c1 public
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

SOURCE = "snmp"

def build_commands(module):
    commands = []
    config = {}
    config['config'] = parse_config(get_config(module, source=SOURCE))
    config['access'] = parse_config_section(get_config(module, source=SOURCE), 'Access Control Summary:', module.params['index'], 'Access Control #')
    if module.params['enable']:
        if config['config']['snmpv1'] == "disabled" and module.params['enable'] == True:
            commands.append(SOURCE + ' -S enable')
        elif config['config']['snmpv1'] == "enabled" and module.params['enable'] == False:
            commands.append(SOURCE + ' -S disable')
    if module.params['community'] and module.params['index']:
        if config['access']['community'] != module.params['community']:
            commands.append(SOURCE + ' -c' + str(module.params['index']) + ' '  + module.params['community'])
    if module.params['accesstype'] and module.params['index']:
        if config['access']['accesstype'] != module.params['accesstype']:
            commands.append(SOURCE + ' -a' + str(module.params['index']) + ' '  + module.params['accesstype'])
    if module.params['accessaddress'] and module.params['index']:
        if config['access']['address'] != module.params['accessaddress']:
            commands.append(SOURCE + ' -n' + str(module.params['index']) + ' '  + module.params['accessaddress'])
    return commands

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        enable=dict(type='bool'),
        index=dict(type='int', choices=[1, 2, 3, 4]),
        community=dict(type='str'),
        accesstype=dict(type='str', choices=['disabled', 'read', 'write', 'writeplus']),
        accessaddress=dict(type='str')
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           required_by={
                             'community': 'index',
                             'accesstype': 'index',
                             'accessaddress': 'index',
                           },
                           supports_check_mode=True)

    warnings = list()
    #warnings = json.dumps(build_commands(module))

    result = {'changed': False}

    if warnings:
        result['warnings'] = warnings

    commands = []
    commands = build_commands(module)
    #result['debug'] = parse_config(get_config(module, source=SOURCE))
    #result['debug2'] = parse_config_section(get_config(module, source=SOURCE), 'Access Control Summary:', 1, "Access Control #")

    result['commands'] = commands

    if commands:
        if not module.check_mode:
            load_config(module, commands)

        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
