# fabric 1.9.0
from fabric.operations import local
from fabric.api import env


'''
This file is collection of commands regarding deployment
'''

env.user = 'oursky'
env.roledefs.update({
    'oursky': ['oursky'],
    'skygear': ['skygeario'],
})
config = '/home/faseng/.docker'


# Heaven will execute fab -R edge deploy:branch_name=edge
def deploy(branch_name):
    print("Executing on %s as %s" % (env.host, env.user))
    if branch_name == 'master':
        tag = 'latest'
        onbuild = 'onbuild'
    elif branch_name[0] == 'v':
        # Tag is in format of v0.1.0, but docker convention is 0.1.0
        tag = branch_name[1:]
        onbuild = branch_name[1:] + '-onbuild'
    else:
        print("Brnach name not in supported format")
        return

    local('docker build -t %s/py-skygear:%s .' % (
        env.host,
        tag
    ))
    local('docker build -t %s/py-skygear:%s -f Dockerfile-onbuild .' % (
        env.host,
        onbuild
    ))
    local('docker --config=%s push %s/py-skygear:%s' % (
        config,
        env.host,
        tag
    ))
    local('docker --config=%s push %s/py-skygear:%s' % (
        config,
        env.host,
        onbuild
    ))
