# fabric 1.9.0
from fabric.operations import local
from fabric.api import env


'''
This file is collection of commands regarding deployment
'''

env.user = 'oursky'
env.roledefs.update({
    'hub': ['hub.docker.com'],
})

# Heaven will execute fab -R edge deploy:branch_name=edge
def deploy(branch_name):
    print("Executing on %s as %s" % (env.host, env.user))
    local('docker build -t oursky/py-skygear:latest .')
    local('docker build -t oursky/py-skygear:onbuild -f Dockerfile-onbuild .')
    local('docker --config=/home/faseng/.docker push oursky/py-skygear:latest')
    local('docker --config=/home/faseng/.docker push oursky/py-skygear:onbuild')
