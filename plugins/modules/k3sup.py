#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: k3sup
short_description: Install k3s servers and agent on local or remote hosts
description:
    - Install k3s servers and agent on local or remote hosts.
author: "Ivan Vandot"
requirements:
  - "python >= 2.6"
options:
  action:
    description:
    - Install k3s on server or agent node
    type: str
    required: true
    choices:
    - server
    - agent
  k3sup_bin:
    description:
    - Path to k3sup binary
    type: path
    default: /usr/local/bin/k3sup
  ip:
    description:
    - Public IP of node
    type: str
    default: 127.0.0.1
  user:
    description:
    - Username for SSH login
    type: str
    default: root
  sudo:
    description:
    - Use sudo for installation
    type: bool
    default: true
  server:
    description:
    - Join the cluster as a server rather than as an agent
    - Available only for agent (join) action
    type: bool
    default: false
  server_ip:
    description:
    - Public IP of existing k3s server
    type: str
  server_ssh_port:
    description:
    - The port on which to connect to server for ssh
    type: int
    default: 22
  server_user:
    description:
    - Server username for SSH login
    type: str
    default: root
  cluster:
    description:
    - Start this server in clustering mode, for use with dqlite (embedded HA)
    type: bool
    default: false
  datastore:
    description:
    - Connection-string for the k3s datastore to enable HA
    - i.e. "mysql://username:password@tcp(hostname:3306)/database-name"
    type: str
  skip_install:
    description:
    - If you already have k3s installed, you can just run this command to get the kubeconfig
    type: bool
    default: false
  ssh_key:
    description:
    - Specify a specific path for the SSH key for remote login
    type: str
    default: ~/.ssh/id_rsa
  local_path:
    description:
    - Set the file where you want to save your cluster's kubeconfig
    type: str
    default: ./kubeconfig
  merge:
    description:
    - Merge config into existing file instead of overwriting (e.g. to add config to the default kubectl config, use --local-path ~/.kube/config --merge)
    type: bool
    default: false
  context:
    description:
    - Set the name of the kubeconfig context
  ssh_port:
    description:
    - Specify an alternative port for ssh
    type: int
    default: 22
  k3s_extra_args:
    description:
    - Optional extra arguments to pass to k3s installer, wrapped in quotes, i.e. --k3s-extra-args '--no-deploy traefik' or --k3s-extra-args '--docker'. For multiple args combine then within single quotes --k3s-extra-args '--no-deploy traefik --docker'
    type: str
  k3s_version:
    description:
    - Set the specific version of k3s, i.e. v0.9.1
    type: str
  ipsec:
    description:
    - Enforces the optional extra argument for k3s: --flannel-backend option: ipsec
    type: bool
    default: false
'''


EXAMPLES = r'''
- name: Install k3s on remote host
    vandot.k3sup.k3sup:
    action: server
    ip: "1.1.1.1"
    ssh_key: "~/.ssh/id_ed25519"
'''


RETURN = r'''
data:
    description: k3sup action status
    returned: success
    type: dict
    sample: {
        changed=True/False,
        cmd="k3sup install --ip 1.1.1.1 --user root --ssh-key ~/.ssh/id_ed25519 ...",
        action="server",
        ip="1.1.1.1",
        stdout="stdout of executed cmd",
        stderr="stderr of executed cmd"
    }
'''

import os
from ansible.module_utils.basic import AnsibleModule


def install(module, k3sup_bin, action, ip, local_path, local, merge,
            ssh_key, ssh_port, user, server_ip, server_ssh_port,
            server_user, server, cluster, datastore, sudo, skip_install,
            no_extras, context, k3s_extra_args, k3s_version, ipsec):
    if action == "server":
        action = "install"
    elif action == "agent":
        action = "join"
    cmd_args = [k3sup_bin, action, "--ip", ip,
                "--local-path", local_path, "--ssh-key", ssh_key,
                "--ssh-port", str(ssh_port), "--user", user]
    if action == "install":
        cmd_args.extend(["--context", context])
    if merge:
        cmd_args.append("--local")
    if merge:
        cmd_args.append("--merge")
    if server_ip:
        cmd_args.extend(["--server-ip", server_ip])
    if server_ssh_port:
        cmd_args.extend(["--server-ssh-port", str(server_ssh_port)])
    if server_user:
        cmd_args.extend(["--server-user", server_user])
    if server:
        cmd_args.append("--server")
    if cluster:
        cmd_args.append("--cluster")
    if datastore:
        cmd_args.extend(["--datastore", datastore])
    if sudo:
        cmd_args.append("--sudo")
    if skip_install:
        cmd_args.append("--skip-install")
    if no_extras:
        cmd_args.append("--no-extras")
    if k3s_extra_args:
        cmd_args.extend(["--k3s-extra-args", k3s_extra_args])
    if k3s_version:
        cmd_args.extend(["--k3s-version", k3s_version])
    if ipsec:
        cmd_args.append("--ipsec")

    cmd = " ".join(cmd_args)

    if module.check_mode:
        return True, cmd, "check mode", ""

    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to install %s: %s" % (action, err))

    return True, cmd, out, err


def is_cluster_installed(module, k3sup_bin, action, ip, local_path,
                         local, merge, ssh_key, ssh_port, user,
                         server_ip, server_ssh_port, server_user):
    if action == "server":
        action = "install"
    elif action == "agent":
        action = "join"
    cmd_args = [k3sup_bin, action, "--skip-install", "--ip", ip,
                "--local-path", local_path, "--ssh-key", ssh_key,
                "--ssh-port", str(ssh_port), "--user", user]
    if merge:
        cmd_args.append("--local")
    if merge:
        cmd_args.append("--merge")
    if server_ip:
        cmd_args.extend(["--server-ip", server_ip])
    if server_ssh_port:
        cmd_args.extend(["--server-ssh-port", str(server_ssh_port)])
    if server_user:
        cmd_args.extend(["--server-user", server_user])

    cmd = " ".join(cmd_args)

    rc, out, err = module.run_command(cmd)
    if rc == 1:
        return False

    return True


def main():

    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, choices=['server', 'agent'],
                        type='str'),
            k3sup_bin=dict(required=False, default="/usr/local/bin/k3sup",
                           type="path"),
            cluster=dict(required=False, default=False, type="bool"),
            datastore=dict(required=False, default=None, type="str"),
            ip=dict(required=False, default="127.0.0.1", type="str"),
            user=dict(required=False, default="root", type="str"),
            sudo=dict(required=False, default=True, type="bool"),
            skip_install=dict(required=False, default=False, type="bool"),
            ssh_key=dict(required=False, default="~/.ssh/id_rsa", type="str"),
            local_path=dict(required=False, default="./kubeconfig",
                            type="str"),
            local=dict(required=False, default=False, type="bool"),
            merge=dict(required=False, default=False, type="bool"),
            no_extras=dict(required=False, default=False, type="bool"),
            context=dict(required=False, default="default", type="str"),
            ssh_port=dict(required=False, default=22, type="int"),
            k3s_extra_args=dict(required=False, default=None, type="str"),
            k3s_version=dict(required=False, default=None, type="str"),
            ipsec=dict(required=False, default=False, type="bool"),
            server=dict(required=False, default=False, type="bool"),
            server_ip=dict(required=False, default=None, type="str"),
            server_ssh_port=dict(required=False, default=None, type="int"),
            server_user=dict(required=False, default=None, type="str")
        ),
        supports_check_mode=True
    )

    action = module.params["action"]
    k3sup_bin = module.params["k3sup_bin"]
    cluster = module.params["cluster"]
    datastore = module.params["datastore"]
    ip = module.params["ip"]
    user = module.params["user"]
    sudo = module.params["sudo"]
    skip_install = module.params["skip_install"]
    ssh_key = module.params["ssh_key"]
    local_path = module.params["local_path"]
    local = module.params["local"]
    merge = module.params["merge"]
    no_extras = module.params["no_extras"]
    context = module.params["context"]
    ssh_port = module.params["ssh_port"]
    k3s_extra_args = module.params["k3s_extra_args"]
    k3s_version = module.params["k3s_version"]
    ipsec = module.params["ipsec"]
    server = module.params["server"]
    server_ip = module.params["server_ip"]
    server_ssh_port = module.params["server_ssh_port"]
    server_user = module.params["server_user"]

    changed, cmd, out, err = False, '', '', ''

    if not (os.path.isfile(k3sup_bin) and os.access(k3sup_bin, os.X_OK)):
        module.fail_json(msg='k3sup binary required: \
                         https://github.com/vandot/ansible-role-k3sup')

    is_installed = is_cluster_installed(module, k3sup_bin, action, ip,
                                        local_path, local, merge, ssh_key,
                                        ssh_port, user, server_ip,
                                        server_ssh_port, server_user)

    if is_installed:
        module.exit_json(changed=False, action=action, ip=ip)

    if action in ["server", "agent"]:
        changed, cmd, out, err = install(module, k3sup_bin, action, ip,
                                         local_path, local, merge,
                                         ssh_key, ssh_port, user,
                                         server_ip, server_ssh_port,
                                         server_user, server, cluster,
                                         datastore, sudo, skip_install,
                                         no_extras, context,
                                         k3s_extra_args, k3s_version,
                                         ipsec)

    module.exit_json(changed=changed, cmd=cmd, action=action, ip=ip,
                     stdout=out, stderr=err)


if __name__ == '__main__':
    main()
