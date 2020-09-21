# Ansible Collection: k3sup

This repository contains sample code for automating k3sup installation and management using Ansible.

[Ansible](https://www.ansible.com/) is a radically simple IT automation engine that automates cloud provisioning, configuration management, application deployment, intra-service orchestration, and many other IT needs.
[k3sup](https://k3sup.dev/) is a light-weight utility to get from zero to KUBECONFIG with [k3s](https://k3s.io/) on any local or remote VM. All you need is `ssh` access and the `k3sup` binary to get `kubectl` access immediately.

## Installation

`ansible-galaxy collection install vandot.k3sup`

## Example

Start three nodes cluster on DO

```
---
- hosts: localhost
  gather_facts: true
  connection: local

  tasks:
    - name: Create ssh key
      community.digitalocean.digital_ocean_sshkey:
        oauth_token: "{{ oauth_token }}"
        name: mykey
        ssh_pub_key: "{{ lookup('file', '~/.ssh/id_ed25519.pub') }}"
        state: present
      register: ssh_key

    - name: Create server
      community.digitalocean.digital_ocean_droplet:
        state: present
        name: k3s-server
        oauth_token: "{{ oauth_token }}"
        size: 2gb
        region: fra1
        image: ubuntu-20-04-x64
        wait_timeout: 500
        ssh_keys:
          - "{{ ssh_key.data.ssh_key.fingerprint }}"
        tags:
          - "server"
          - "k3sup"
      register: k3s_server

    - name: Create agents
      community.digitalocean.digital_ocean_droplet:
        state: present
        name: "{{ item }}"
        oauth_token: "{{ oauth_token }}"
        size: 2gb
        region: fra1
        image: ubuntu-20-04-x64
        wait_timeout: 500
        ssh_keys:
          - "{{ ssh_key.data.ssh_key.fingerprint }}"
        tags:
          - "agent"
          - "k3sup"
      register: k3s_agent
      with_items:
        - k3s-agent1
        - k3s-agent2

    - name: Install k3s server on k3s-server
      vandot.k3sup.k3sup:
        action: server
        ip: "{{ k3s_server.data.ip_address }}"
        ssh_key: "~/.ssh/id_ed25519"

    - name: Install k3s agent on k3s-agents
      vandot.k3sup.k3sup:
        action: agent
        ip: "{{ item.data.ip_address }}"
        server_ip: "{{ k3s_server.data.ip_address }}"
        ssh_key: "~/.ssh/id_ed25519"
      with_items:
        - "{{k3s_agent.results}}"
```