#!/usr/bin/python
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: apc_dns
author: "Matt Haught (@haught)"
short_description: Manage dns configuration on APC devices.
description:
  - This module provides declarative management of APC dns
    on APC UPS NMC systems.
notes:
  - Tested APC NMC v3 (AP9641) running APC OS v1.4.2.1
options:
  primarydnsserver:
    description:
      - Set the primary DNS server.
    type: str
  secondarydnsserver:
    description:
      - Set the secondary DNS server.
    type: str
  domainname:
    description:
      - Set the domain name
    type: str
  domainnameipv6:
    description:
      - Set the domain name IPv6.
    type: str
  systemnamesync:
    description:
      - Synchronizes the system name and the hostname.
    type: bool
  overridemanualdnssettings:
    description:
      - Override the manual DNS.
    type: bool
'''

EXAMPLES = """
- name: Set dns name
  ncstate.network.apc_dns:
    primarydns: "1.1.1.1"

- name: Set two dns settings
  ncstate.network.apc_dns:
    primarydns: "1.1.1.1"
    secondarydns: "4.4.4.4"
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - dns -n ups001
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

SOURCE = "dns"

def build_commands(module):
    commands = []
    config = parse_config(get_config(module, source=SOURCE))
    if module.params['primarydnsserver']:
        if config['primarydnsserver'] != module.params['primarydnsserver']:
            commands.append(SOURCE + ' -p ' + module.params['primarydnsserver'])
    if module.params['secondarydnsserver']:
        if config['secondarydnsserver'] != module.params['secondarydnsserver']:
            commands.append(SOURCE + ' -s ' + module.params['secondarydnsserver'])
    if module.params['domainname']:
        if config['domainname'] != module.params['domainname']:
            commands.append(SOURCE + ' -d ' + module.params['domainname'])
    if module.params['domainnameipv6']:
        if config['domainnameipv6'] != module.params['domainnameipv6']:
            commands.append(SOURCE + ' -n ' + module.params['domainnameipv6'])
    if module.params['hostname']:
        if config['hostname'] != module.params['hostname']:
            commands.append(SOURCE + ' -h ' + module.params['hostname'])
    if module.params['systemnamesync']:
        if config['systemnamesync'] == "Disabled" and module.params['systemnamesync'] == True:
            commands.append(SOURCE + ' -y enable')
        elif config['systemnamesync'] == "Enabled" and module.params['systemnamesync'] == False:
            commands.append(SOURCE + ' -y disable')
    if module.params['overridemanualdnssettings']:
        if config['overridemanualdnssettings'] == "Disabled" and module.params['overridemanualdnssettings'] == True:
            commands.append(SOURCE + ' -OM enable')
        elif config['overridemanualdnssettings'] == "Enabled" and module.params['overridemanualdnssettings'] == False:
            commands.append(SOURCE + ' -OM disable')
    return commands

def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        primarydnsserver=dict(type='str'),
        secondarydnsserver=dict(type='str'),
        domainname=dict(type='str'),
        domainnameipv6=dict(type='str'),
        hostname=dict(type='str'),
        systemnamesync=dict(type='bool'),
        overridemanualdnssettings=dict(type='bool')
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
