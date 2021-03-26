#!/usr/bin/python
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: apc_system
author: "Matt Haught (@haught)"
short_description: Manage system configuration on APC devices.
description:
  - This module provides declarative management of APC system
    on APC UPS systems.
notes:
  - Tested against Smart-UPS SRT 1500 with APC OS v6.8.2
options:
  name:
    description:
      - System system name of device.
    type: str
  contact:
    description:
      - Contact name for device.
    type: str
  location:
    description:
      - Location of device.
    type: str
  message:
    description:
      - Show a custom message on the logon page of the web UI or the CLI.
    type: str
  hostnamesync:
    description:
      - Synchronize the system and the hostname.
    type: bool
'''

EXAMPLES = """
- name: Set system name
  ncstate.network.apc_system:
    name: "device01"

- name: Set two system settings
  ncstate.network.apc_system:
    name: "device01"
    location: "Bldg 101"
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - system -l Bldg 101
"""
import re
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import CustomNetworkConfig
from ansible_collections.ncstate.network.plugins.module_utils.network.apc import (
    load_config,
    get_config,
    parse_config,
)

SOURCE = "system"

def build_commands(module):
    commands = []
    config = parse_config(get_config(module, source=SOURCE))
    if module.params['name']:
        if config['name'] != module.params['name']:
            commands.append(SOURCE + ' -n ' + module.params['name'])
    if module.params['contact']:
        if config['contact'] != module.params['contact']:
            commands.append(SOURCE + ' -c ' + module.params['contact'])
    if module.params['location']:
        if config['location'] != module.params['location']:
            commands.append(SOURCE + ' -l ' + module.params['location'])
    if module.params['message']:
        if config['message'] != module.params['message']:
            commands.append(SOURCE + ' -m ' + module.params['message'])
    if module.params['hostnamesync']:
        if config['hostnamesync'] == "Disabled" and module.params['hostnamesync'] == True:
            commands.append(SOURCE + ' -s enable')
        elif config['hostnamesync'] == "Enabled" and module.params['hostnamesync'] == False:
            commands.append(SOURCE + ' -s disable')
    return commands

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        name=dict(type='str'),
        contact=dict(type='str'),
        location=dict(type='str'),
        message=dict(type='str'),
        hostnamesync=dict(type='bool', default=False)
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    warnings = list()

    result = {'changed': False}

    if warnings:
        result['warnings'] = warnings

    commands = build_commands(module)

    result['commands'] = commands

    if commands:
        if not module.check_mode:
            load_config(module, commands)

        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
