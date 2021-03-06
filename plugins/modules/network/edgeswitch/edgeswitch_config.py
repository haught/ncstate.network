#!/usr/bin/python
#
# Copyright: Ansible Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: edgeswitch_config
author:
  - "Matt Haught (@haught)"
  - "James Mighion (@jmighion)"
short_description: Manage Edgeswitch configuration sections
description:
  - Edgeswitch configurations use a flat nonindented file syntax
    for segmenting configuration into sections.  This module provides
    an implementation for working with Edgeswitch configuration sections
    in a deterministic way.

options:
  lines:
    description:
      - The ordered set of commands that should be configured in the
        section.  The commands must be the exact same commands as found
        in the device running-config.  Be sure to note the configuration
        command syntax as some commands are automatically modified by the
        device config parser.
    aliases: ['commands']
    type: list
    elements: str
  parents:
    description:
      - The ordered set of parents that uniquely identify the section or hierarchy
        the commands should be checked against.  If the parents argument
        is omitted, the commands are checked against the set of top
        level or global commands.
    type: list
    elements: str
  src:
    description:
      - Specifies the source path to the file that contains the configuration
        or configuration template to load.  The path to the source file can
        either be the full path on the Ansible control host or a relative
        path from the playbook or role root directory.  This argument is mutually
        exclusive with I(lines), I(parents).
    type: path
  before:
    description:
      - The ordered set of commands to push on to the command stack if
        a change needs to be made.  This allows the playbook designer
        the opportunity to perform configuration commands prior to pushing
        any changes without affecting how the set of commands are matched
        against the system.
    type: list
    elements: str
  after:
    description:
      - The ordered set of commands to append to the end of the command
        stack if a change needs to be made.  Just like with I(before) this
        allows the playbook designer to append a set of commands to be
        executed after the command set.
    type: list
    elements: str
  match:
    description:
      - Instructs the module on the way to perform the matching of
        the set of commands against the current device config.  If
        match is set to I(line), commands are matched line by line.  If
        match is set to I(strict), command lines are matched with respect
        to position.  If match is set to I(exact), command lines
        must be an equal match.  Finally, if match is set to I(none), the
        module will not attempt to compare the source configuration with
        the running configuration on the remote device.
    default: line
    choices: ['line', 'strict', 'exact', 'none']
    type: str
  replace:
    description:
      - Instructs the module on the way to perform the configuration
        on the device.  If the replace argument is set to I(line) then
        the modified lines are pushed to the device in configuration
        mode.  If the replace argument is set to I(block) then the entire
        command block is pushed to the device in configuration mode if any
        line is not correct.
    default: line
    choices: ['line', 'block']
    type: str
  backup:
    description:
      - This argument will cause the module to create a full backup of
        the current C(running-config) from the remote device before any
        changes are made. If the C(backup_options) value is not given,
        the backup file is written to the C(backup) folder in the playbook
        root directory. If the directory does not exist, it is created.
    type: bool
    default: 'no'
  running_config:
    description:
      - The module, by default, will connect to the remote device and
        retrieve the current running-config to use as a base for comparing
        against the contents of source.  There are times when it is not
        desirable to have the task get the current running-config for
        every task in a playbook.  The I(running_config) argument allows the
        implementer to pass in the configuration to use as the base
        config for comparison.
    aliases: ['config']
    type: str
  save_when:
    description:
      - When changes are made to the device running-configuration, the
        changes are not copied to non-volatile storage by default.  Using
        this argument will change that before.  If the argument is set to
        I(always), then the running-config will always be copied to the
        startup configuration and the I(modified) flag will always be set to
        True.  If the argument is set to I(modified), then the running-config
        will only be copied to the startup configuration if it has changed since
        the last save to startup configuration.  If the argument is set to
        I(never), the running-config will never be copied to the
        startup configuration.  If the argument is set to I(changed), then the running-config
        will only be copied to the startup configuration if the task has made a change.
    default: never
    choices: ['always', 'never', 'modified', 'changed']
    type: str
  diff_against:
    description:
      - When using the C(ansible-playbook --diff) command line argument
        the module can generate diffs against different sources.
      - When this option is configure as I(startup), the module will return
        the diff of the running-config against the startup configuration.
      - When this option is configured as I(intended), the module will
        return the diff of the running-config against the configuration
        provided in the C(intended_config) argument.
      - When this option is configured as I(running), the module will
        return the before and after diff of the running-config with respect
        to any changes made to the device configuration.
    choices: ['startup', 'intended', 'running']
    type: str
  diff_ignore_lines:
    description:
      - Use this argument to specify one or more lines that should be
        ignored during the diff.  This is used for lines in the configuration
        that are automatically updated by the system.  This argument takes
        a list of regular expressions or exact line matches.
    type: list
    elements: str
  intended_config:
    description:
      - The C(intended_config) provides the master configuration that
        the node should conform to and is used to check the final
        running-config against.   This argument will not modify any settings
        on the remote device and is strictly used to check the compliance
        of the current device's configuration against.  When specifying this
        argument, the task should also modify the C(diff_against) value and
        set it to I(intended).
    type: str
  backup_options:
    description:
      - This is a dict object containing configurable options related to backup file path.
        The value of this option is read only when C(backup) is set to I(yes), if C(backup) is set
        to I(no) this option will be silently ignored.
    suboptions:
      filename:
        description:
          - The filename to be used to store the backup configuration. If the filename
            is not given it will be generated based on the hostname, current time and date
            in format defined by <hostname>_config.<current-date>@<current-time>
        type: str
      dir_path:
        description:
          - This option provides the path ending with directory name in which the backup
            configuration file will be stored. If the directory does not exist it will be first
            created and the filename is either the value of C(filename) or default filename
            as described in C(filename) options description. If the path value is not given
            in that case a I(backup) directory will be created in the current working directory
            and backup configuration will be copied in C(filename) within I(backup) directory.
        type: path
    type: dict

notes:
  - Tested against EdgeSwitch 1.9.2
'''

EXAMPLES = """
- name: Configure top level configuration
  ncstate.network.edgeswitch_config:
    lines: domain-name example.net

- name: Diff the running-config against a provided config
  ncstate.network.edgeswitch_config:
    diff_against: intended
    intended_config: "{{ lookup('file', 'master.cfg') }}"

- name: Configure interface settings
  ncstate.network.edgeswitch_config:
    lines:
      - description test interface
      - ip access-group EXAMPLE in
    parents: interface 0/1

- name: Load new acl into device
  ncstate.network.edgeswitch_config:
    lines:
      - deny tcp 10.0.1.0 0.0.255.255 host 10.10.10.10 eq 443
      - permit ip any any
    parents: ip access-list EXAMPLE
    before: no ip access-list EXAMPLE
    match: exact

- name: Configurable backup path
  ncstate.network.edgeswitch_config:
    backup: yes
    lines: domain-name example.net
    backup_options:
      filename: backup.cfg
      dir_path: /home/user
"""

RETURN = """
commands:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['domain-name example.net', 'vlan database', 'vlan name 932 "VLAN 932"']
updates:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['domain-name example.net', 'vlan database', 'vlan name 932 "VLAN 932"']
backup_path:
  description: The full path to the backup file
  returned: when backup is yes
  type: str
  sample: /playbooks/ansible/backup/edgeswitch_config.2016-07-16@22:28:34
"""

import re

from ansible_collections.community.network.plugins.module_utils.network.edgeswitch.edgeswitch import run_commands, get_config, load_config
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import NetworkConfig, dumps


def get_running_config(module, config=None):
    contents = module.params['running_config']
    if not contents:
        if config:
            contents = config
        else:
            contents = get_config(module)
    return NetworkConfig(contents=indent_config(contents))


def indent_config(config):
    """ indent the config so we can modify sections natively
    """
    parent_re = [
        re.compile(r"^(?:vlan\sdatabase)$"),
        re.compile(r"^(?:ip\saccess-list\s\S+)$"),
        re.compile(r"^(?:line\s\S+)$"),
        re.compile(r"^(?:interface\s\S+)$"),
        re.compile(r"^(?:interface\slag\s\S+)$"),
        re.compile(r"^(?:service\s\S+)$"),
    ]
    config_indented = list()
    indent = False
    for line in str(config).split("\n"):
        if any(regex.match(line) for regex in parent_re):
            config_indented.append(line)
            indent = True
        elif line == 'exit':
            config_indented.append(line)
            indent = False
        else:
            config_indented.append(" %s" % line if indent else line)
    return "\n".join(config_indented)


def get_candidate(module):
    candidate = NetworkConfig()

    if module.params['src']:
        candidate.load(module.params['src'])
    elif module.params['lines']:
        parents = module.params['parents'] or list()
        candidate.add(module.params['lines'], parents=parents)
    return candidate


def save_config(module, result):
    result['changed'] = True
    if not module.check_mode:
        run_commands(module, {'command': 'write memory', 'prompt': 'Are you sure you want to save', 'answer': 'y'})
    else:
        module.warn('Skipping command `write memory` '
                    'due to check_mode.  Configuration not copied to '
                    'non-volatile storage')


def main():
    """ main entry point for module execution
    """
    backup_spec = dict(
        filename=dict(),
        dir_path=dict(type='path')
    )
    argument_spec = dict(
        src=dict(type='path'),

        lines=dict(aliases=['commands'], type='list', elements='str'),
        parents=dict(type='list', elements='str'),

        before=dict(type='list', elements='str'),
        after=dict(type='list', elements='str'),

        match=dict(default='line', choices=['line', 'strict', 'exact', 'none']),
        replace=dict(default='line', choices=['line', 'block']),

        running_config=dict(aliases=['config']),
        intended_config=dict(),

        backup=dict(type='bool', default=False),
        backup_options=dict(type='dict', options=backup_spec),

        save_when=dict(choices=['always', 'never', 'modified', 'changed'], default='never'),

        diff_against=dict(choices=['running', 'startup', 'intended']),
        diff_ignore_lines=dict(type='list', elements='str'),
    )

    mutually_exclusive = [('lines', 'src'),
                          ('parents', 'src')]

    required_if = [('match', 'strict', ['lines']),
                   ('match', 'exact', ['lines']),
                   ('replace', 'block', ['lines']),
                   ('diff_against', 'intended', ['intended_config'])]

    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
                           required_if=required_if,
                           supports_check_mode=True)

    warnings = list()

    result = {'changed': False, 'warnings': warnings}

    config = None

    if module.params['backup'] or (module._diff and module.params['diff_against'] == 'running'):
        contents = get_config(module)
        config = NetworkConfig(contents=contents)
        if module.params['backup']:
            result['__backup__'] = contents

    if any((module.params['src'], module.params['lines'])):
        match = module.params['match']
        replace = module.params['replace']

        candidate = get_candidate(module)

        if match != 'none':
            config = get_running_config(module, config)
            path = module.params['parents']
            configobjs = candidate.difference(config, match=match, replace=replace, path=path)
        else:
            configobjs = candidate.items

        if configobjs:
            commands = dumps(configobjs, 'commands').split('\n')

            if module.params['before']:
                commands[:0] = module.params['before']

            if module.params['after']:
                commands.extend(module.params['after'])

            result['commands'] = commands
            result['updates'] = commands

            if not module.check_mode:
                load_config(module, commands)

            result['changed'] = True

    running_config = None
    startup_config = None

    diff_ignore_lines = module.params['diff_ignore_lines']

    if module.params['save_when'] == 'always':
        save_config(module, result)
    elif module.params['save_when'] == 'modified':
        output = run_commands(module, ['show running-config', 'show startup-config'])

        running_config = NetworkConfig(contents=output[0], ignore_lines=diff_ignore_lines)
        startup_config = NetworkConfig(contents=output[1], ignore_lines=diff_ignore_lines)

        # NetworkConfig.sha1 does not ignore lines, so do a difference which does
        diff = running_config.difference(startup_config)
        if diff:
            save_config(module, result)

    elif module.params['save_when'] == 'changed':
        if result['changed']:
            save_config(module, result)

    if module._diff:
        if not running_config:
            output = run_commands(module, 'show running-config')
            contents = output[0]
        else:
            contents = running_config.config_text

        # recreate the object in order to process diff_ignore_lines
        running_config = NetworkConfig(contents=contents, ignore_lines=diff_ignore_lines)

        if module.params['diff_against'] == 'running':
            if module.check_mode:
                module.warn("unable to perform diff against running-config due to check mode")
                contents = None
            else:
                contents = config.config_text

        elif module.params['diff_against'] == 'startup':
            if not startup_config:
                output = run_commands(module, 'show startup-config')
                contents = output[0]
            else:
                contents = startup_config.config_text

        elif module.params['diff_against'] == 'intended':
            contents = module.params['intended_config']

        if contents is not None:
            base_config = NetworkConfig(contents=contents, ignore_lines=diff_ignore_lines)

            if running_config.sha1 != base_config.sha1:
                result.update({
                    'changed': True,
                    'diff': {'before': str(base_config), 'after': str(running_config)}
                })

    module.exit_json(**result)


if __name__ == '__main__':
    main()
