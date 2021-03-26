#!/usr/bin/python
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: apc_radius
author: "Matt Haught (@haught)"
short_description: Manage radius configuration on APC devices.
description:
  - This module provides declarative management of APC radius
    on APC UPS systems.
notes:
  - Tested against Smart-UPS SRT 1500 with APC OS v6.8.2
options:
  access:
    description:
      - Authentication type of local, radiuslocal, and radius. A value of "local" disables radius,
        while "radiuslocal" tries radius first and then falls back to local, and "radius" only
        authenticates to radius.
    type: str
    choices: ['local', 'radiuslocal', 'radius']
  primaryserver:
    description:
      - Primary radius server ip.
    type: str
  primaryport:
    description:
      - Primary radius server port.
    type: str
  primarysecret:
    description:
      - Primary radius authentication shared secret.
    type: str
  primarytimeout:
    description:
      - Primary radius authentication timeout.
    type: str
  secondaryserver:
    description:
      - Secondary radius server ip.
    type: str
  secondaryport:
    description:
      - Secondary radius server port.
    type: str
  secondarysecret:
    description:
      - Secondary radius authentication shared secret.
    type: str
  secondarytimeout:
    description:
      - Secondary radius authentication timeout.
    type: str
  forcepwchange:
    description:
      - Force a password change
    type: bool
'''

EXAMPLES = """
- name: Set radius name
  ncstate.network.apc_radius:
    primaryip: "10.1.1.1"

- name: Set two radius settings
  ncstate.network.apc_radius:
    primaryip: "10.1.1.1"
    secondaryip: "10.4.4.4"
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - radius -a radiuslocal
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

SOURCE = "radius"

def build_commands(module):
    commands = []
    config = parse_config(get_config(module, source=SOURCE))
    if module.params['access']:
        if config['access'] != module.params['access']:
            commands.append(SOURCE + ' -a ' + module.params['access'])
    if module.params['primaryserver']:
        if config['primaryserver'] != module.params['primaryserver']:
            commands.append(SOURCE + ' -p1 ' + module.params['primaryserver'])
        if config['primaryserver'] != module.params['primaryserver'] or module.params['forcepwchange'] == True:
            if module.params['primarysecret']:
                if config['primaryserversecret'] != module.params['primarysecret']:
                    commands.append(SOURCE + ' -s1 ' + module.params['primarysecret'])
    if module.params['primaryport']:
        if config['primaryserverport'] != module.params['primaryport']:
            commands.append(SOURCE + ' -o1 ' + str(module.params['primaryport']))
    if module.params['primarytimeout']:
        if config['primaryservertimeout'] != module.params['primarytimeout']:
            commands.append(SOURCE + ' -t1 ' + str(module.params['primarytimeout']))
    if module.params['secondaryserver']:
        if config['secondaryserver'] != module.params['secondaryserver']:
            commands.append(SOURCE + ' -p2 ' + module.params['secondaryserver'])
        if config['secondaryserver'] != module.params['secondaryserver'] or module.params['forcepwchange'] == True:
            if module.params['secondarysecret']:
                if config['secondaryserversecret'] != module.params['secondarysecret']:
                    commands.append(SOURCE + ' -s2 ' + module.params['secondarysecret'])
    if module.params['secondaryport']:
        if config['secondaryserverport'] != module.params['secondaryport']:
            commands.append(SOURCE + ' -o2 ' + str(module.params['secondaryport']))
    if module.params['secondarytimeout']:
        if config['secondaryservertimeout'] != module.params['secondarytimeout']:
            commands.append(SOURCE + ' -t2 ' + str(module.params['secondarytimeout']))
    return commands

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        access=dict(type='str', choices=['local', 'radiuslocal', 'radius']),
        primaryserver=dict(type='str'),
        primaryport=dict(type='int'),
        primarysecret=dict(type='str'),
        primarytimeout=dict(type='int'),
        secondaryserver=dict(type='str'),
        secondaryport=dict(type='int'),
        secondarysecret=dict(type='str'),
        secondarytimeout=dict(type='int'),
        forcepwchange=dict(type=bool, default=False)
    )

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    warnings = list()
    #warnings = json.dumps(build_commands(module))

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
