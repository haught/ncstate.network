# Ansible Collection - ncstate.network

This is a collection of modules I am workong on that I may one day merge into official repos once all the bugs are worked out.


## Modules
[ncstate.network.tftp_send](plugins/modules/tftp_send.py) - A simple module to take given text and send it as a file to a TFTP server. We are using it to send 'show run' output to backup server when device tftp is not available.

[ncstate.network.edgeswitch_command](plugins/modules/edgeswitch_command.py) - A module to run commands on Ubiquiti EdgeSwitch devices. Wrote this for a PoC for using some of their switches.

[ncstate.network.edgeswitch_config](plugins/modules/edgeswitch_config.py) - A module to configure Ubiquiti EdgeSwitch devices. Wrote this for a PoC for using some of their switches.


