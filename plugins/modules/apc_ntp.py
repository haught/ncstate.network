#!/usr/bin/python
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: apc_ntp
author: "Matt Haught (@haught)"
short_description: Manage ntp configuration on APC devices.
description:
  - This module provides declarative management of APC ntp
    on APC UPS NMC systems.
notes:
  - Tested APC NMC v3 (AP9641) running APC OS v1.4.2.1
options:
  enable:
    description:
      - Enable ntp on device.
    type: bool
  primaryserver:
    description:
      - Primary ntp server ip.
    type: str
  secondaryserver:
    description:
      - Secondary ntp server ip.
    type: str
  overridemanual:
    description:
      - Override the manual time settings.
    type: bool
'''

EXAMPLES = """
- name: Set ntp name
  ncstate.network.apc_ntp:
    primaryip: "10.1.1.1"

- name: Set two ntp settings
  ncstate.network.apc_ntp:
    enable: True
    primaryip: "10.1.1.1"
    secondaryip: "10.4.4.4"
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - ntp -a ntplocal
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

SOURCE = "ntp"

def build_commands(module):
    commands = []
    commands = []
    config = parse_config(get_config(module, source=SOURCE))
    if module.params['enable']:
        if config['ntpstatus'] == "Disabled" and module.params['enable'] == True:
            commands.append(SOURCE + ' -e enable')
        elif config['ntpstatus'] == "Enabled" and module.params['enable'] == False:
            commands.append(SOURCE + ' -e disable')
    if module.params['primaryserver']:
        if config['primaryntpserver'] != module.params['primaryserver']:
            commands.append(SOURCE + ' -p ' + module.params['primaryserver'])
    if module.params['secondaryserver']:
        if config['secondaryntpserver'] != module.params['secondaryserver']:
            commands.append(SOURCE + ' -s ' + module.params['secondaryserver'])
    if module.params['overridemanual']:
        if config['overridemanualntpsettings'] == "disabled" and module.params['overridemanual'] == True:
            commands.append(SOURCE + ' -OM enable')
        elif config['overridemanualntpsettings'] == "enabled" and module.params['overridemanual'] == False:
            commands.append(SOURCE + ' -OM disable')
    return commands

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        enable=dict(type='bool'),
        primaryserver=dict(type='str'),
        secondaryserver=dict(type='str'),
        overridemanual=dict(type='bool', default=False)
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
