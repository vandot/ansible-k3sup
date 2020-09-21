# Ansible Role: k3sup

Ansible role for installing [k3sup](https://k3sup.dev/) a light-weight utility to get from zero to KUBECONFIG with [k3s](https://k3s.io/) on any local or remote VM.

## Requirements

No special requirements.

## Role Variables

| Variable                       | Description                                                              | Default Value                      |
|--------------------------------|--------------------------------------------------------------------------|------------------------------------|
| `k3sup_state`                  | k3sup state, options: installed, uninstalled                             | installed                          |
| `k3sup_release_version`        | Use a specific version of k3sup, eg. `0.9.6`. Specify `false` for latest | `false`                            |
| `k3sup_github_url`             | Set the GitHub URL to install k3sup from                                 | https://github.com/alexellis/k3sup |
| `k3sup_install_dir`            | Installation directory for k3sup                                         | `/usr/local/bin`                   |
| `k3sup_non_root`               | Install k3sup as non-root user. See notes below                          | `false`                            |

#### Important note about `k3sup_release_version`

If you do not set a `k3sup_release_version` the latest version of k3sup will be installed. If you need a specific version of k3sup you must ensure this is set in your Ansible configuration, eg:

```yaml
k3sup_release_version: 0.9.6
```

#### Important note about `k3sup_non_root`

To install k3sup as non root you must not use `become: true`.

`k3sup_install_dir` must be writable by your user.

## Dependencies

No dependencies on other roles.

## Example Playbook

Example playbook:

```yaml
- hosts: servers
  roles:
   - { role: vandot.k3sup.k3sup, k3sup_release_version: 0.9.6 }
```

## License

BSD-3-Clause

## Author Information

[Ivan Vandot](https://ivan.vandot.rs/)
