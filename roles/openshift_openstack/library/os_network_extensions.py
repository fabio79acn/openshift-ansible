#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2018 Red Hat, Inc. and/or its affiliates
# and other contributors as indicated by the @author tags.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# pylint: disable=unused-wildcard-import,wildcard-import,unused-import,redefined-builtin

''' os_network_extensions '''
import keystoneauth1

from ansible.module_utils.basic import AnsibleModule

try:
    import shade
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

DOCUMENTATION = '''
---
module: os_network_extensions_facts
short_description: Retrieve OpenStack Networking extension facts
description:
    - Retrieves all the OpenStack Neutron available extensions
notes:
    - This module creates a new top-level C(openstack_network_extensions) fact
      which contains a list of supported OpenStack Neutron extensions
author:
    - "Antoni Segura Puimedon <antoni@redhat.com>"
'''

RETURN = '''
openstack_network_extensions:
    description: List of available extensions in the Cloud Neutron
    type: list
    returned: always
    sample:
      - agent
      - router
      - subnet_allocation
      - trunk
'''


def main():
    ''' Main module function '''
    module = AnsibleModule(argument_spec={}, supports_check_mode=True)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    try:
        cloud = shade.openstack_cloud()
    # pylint: disable=broad-except
    except Exception:
        module.fail_json(msg='Failed to connect to the cloud')

    try:
        adapter = keystoneauth1.adapter.Adapter(
            session=cloud.keystone_session,
            service_type=cloud.cloud_config.get_service_type('network'),
            interface=cloud.cloud_config.get_interface('network'),
            endpoint_override=cloud.cloud_config.get_endpoint('network'),
            version=cloud.cloud_config.get_api_version('network'))
    # pylint: disable=broad-except
    except Exception:
        module.fail_json(msg='Failed to get an adapter to talk to the Neutron '
                             'API')

    try:
        response = adapter.get('/extensions.json')
    # pylint: disable=broad-except
    except Exception:
        module.fail_json(msg='Failed to retrieve Neutron extensions')

    extensions = []
    try:
        for ext_record in response.json()['extensions']:
            extensions.append(ext_record['alias'])
    # pylint: disable=broad-except
    except Exception:
        module.fail_json(msg='Failed to process cloud networking '
                         'extensions')

    module.exit_json(
        changed=False,
        ansible_facts={'openstack_network_extensions': extensions})


if __name__ == '__main__':
    main()
