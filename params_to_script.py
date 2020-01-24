#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os
import re

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}


# The AnsibleModule object
module = None

class AnsibleModuleError(Exception):
    def __init__(self, results):
        self.results = results


def main():
    module = AnsibleModule(
        argument_spec=dict(
            param_file=dict(type='str'),
            script_file=dict(type='str')
        ),
        supports_check_mode=True
    )

    param_file = module.params['param_file']
    script_file = module.params['script_file']
    changed = False
    script_dict = dict()
    param_dict = dict()
    param_regex = re.compile(r"^\s*\b\w+\b\s+(\w+)=(.*$)")
    script_regex = re.compile(r"\${?\s*\w+\s*}?")
    filedata = ''

    if os.path.exists(param_file):
        if os.path.islink(param_file):
            param_file = os.path.realpath(param_file)
        if not os.access(param_file, os.R_OK) and not os.path.isfile(param_file):
            module.fail_json(msg="Destination %s not readable" % (os.path.dirname(param_file)))
    else:
        if not os.path.exists(os.path.dirname(param_file)):
            try:
                os.stat(os.path.exists(param_file))
            except OSError as e:
                if "permission denied" in to_native(e).lower():
                    module.fail_json(msg="Parameter's file directory %s is not accessible"\
                                         % (os.path.dirname(param_file)))
            module.fail_json(msg="Parameter's file directory %s does not exist" % (os.path.dirname(param_file)))

    if os.path.exists(script_file):
        if os.path.islink(script_file):
            script_file = os.path.realpath(script_file)
        if not os.access(script_file, os.R_OK) and not os.access(script_file, os.W_OK)\
                and not os.path.isfile(script_file):
            module.fail_json(msg="Destination %s not writable" % (os.path.dirname(script_file)))
    else:
        if not os.path.exists(os.path.dirname(script_file)):
            try:
                os.stat(os.path.exists(script_file))
            except OSError as e:
                if "permission denied" in to_native(e).lower():
                    module.fail_json(msg="Script's file directory %s is not accessible"\
                                         % (os.path.dirname(script_file)))
            module.fail_json(msg="Script's file directory %s does not exist" % (os.path.dirname(script_file)))

    with open(param_file, 'r') as fd:
        for line in fd:
            result = param_regex.search(line)
            if result:
                param_dict[result.group(1).strip()] = result.group(2).strip('\"\'')

    with open(script_file, 'r') as fd:
        for line in fd:
            result = script_regex.findall(line)
            if result:
                for var in result:
                    if var not in script_dict:
                        script_dict[re.sub(r'[${}]', '', var).strip()] = var.strip()

    if not param_dict:
        module.fail_json(msg="Module wasn't able to parse parameter's file, dictionary is empty")

    if not script_dict:
        module.fail_json(msg="Module wasn't able to parse variable in script file, dictionary is empty")

    try:
        with open(script_file, 'r') as fd:
            filedata = fd.read()
            for key in script_dict:
                    filedata = filedata.replace(script_dict[key], param_dict[key])
    except KeyError:
        module.fail_json(msg="Variable name mismatching between parameters file and script file")

    if not module.check_mode:
        with open(script_file, 'r+') as fd:
            fd.write(filedata)
        changed = True

    result = dict(changed=changed)
    module.exit_json(**result)

if __name__ == '__main__':
    main()