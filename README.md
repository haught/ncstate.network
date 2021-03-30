# Ansible Collection - ncstate.network

This is a collection of modules for NC State University that have not been submitted to any other projects for inclusion.


## Modules
[ncstate.network.tftp_send](plugins/modules/network/tftp/tftp_send.py) - A simple module to take given text and send it as a file to a TFTP server. It can be used to send 'show run' output to backup server when device tftp is not available.

[ncstate.network.edgeswitch_command](plugins/modules/network/edgeswitch/edgeswitch_command.py) - A module to run commands on Ubiquiti EdgeSwitch devices.

[ncstate.network.edgeswitch_config](plugins/modules/network/edgeswitch/edgeswitch_config.py) - A module to configure Ubiquiti EdgeSwitch devices.

[ncstate.network.apcos_command](plugins/modules/network/apcos/apcos_command.py) - A module to run CLI commands against APC NMCs.

[ncstate.network.apcos_dns](plugins/modules/network/apcos/apcos_dns.py) - A module to configure DNS on APC NMCs.

[ncstate.network.apcos_ntp](plugins/modules/network/apcos/apcos_ntp.py) - A module to configure NTP on APC NMCs.

[ncstate.network.apcos_radius](plugins/modules/network/apcos/apcos_radius.py) - A module to configure RADIUS on APC NMCs.

[ncstate.network.apcos_snmp](plugins/modules/network/apcos/apcos_snmp.py) - A module to configure SNMP v2c on APC NMCs.

[ncstate.network.apcos_snmpv3](plugins/modules/network/apcos/apcos_snmpv3.py) - A module to configure SNMP v3 on APC NMCs.

[ncstate.network.apcos_system](plugins/modules/network/apcos/apcos_system.py) - A module to configure system option on APC NMCs.