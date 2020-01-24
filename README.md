# Ansible module params_to_script
Sometimes there are bash scripts or sql scripts which are using bash env variables.
In order to have ability to run this scripts from Ansible as well as from regular bash script
it is convenient to get variables from usual params file and put them to script:

```bash
# Some comment
export VARIABLE1='VALUE'

# Some comment2
export VARIABLE2="VALUE"
.....

```

in your sql script file:
```
SELECT * FROM ${VARIABLE1} where .... $VARIABLE2 .....
.....
```

This is what this Ansible module is designed for.

```ansible
- name: Change variables in SQL scipt using variable from params file.
  params_to_script:
    script_file: '/home/user/code.sql'
    params_file: '/home/user/params.sh'
```
