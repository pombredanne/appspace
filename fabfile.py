'''appspace fabfile'''

from fabric.api import prompt, local, settings, env


def _test(val):
    truth = val in ['py26', 'py27', 'py32', 'pypy']
    if truth is False:
        raise KeyError(val)
    return val


def tox():
    '''test appspace'''
    local('tox')


def tox_recreate():
    '''recreate appspace test env'''
    prompt(
        'Enter testenv: [py26, py27, py32, pypy]',
        'testenv',
        validate=_test,
    )
    local('tox --recreate -e %(testenv)s' % env)


def release():
    '''release appspace'''
    local('hg update pu')
    local('hg update next')
    local('hg merge pu; hg ci -m automerge')
    local('hg update maint')
    local('hg merge default; hg ci -m automerge')
    local('hg update default')
    local('hg merge next; hg ci -m automerge')
    local('hg update pu')
    local('hg merge default; hg ci -m automerge')
    prompt('Enter tag', 'tag')
    with settings(warn_only=True):
        local('hg tag "%(tag)s"' % env)
        local('hg push ssh://hg@bitbucket.org/lcrees/appspace')
        local('hg push git+ssh://git@github.com:kwarterthieves/appspace.git')
#    local('python setup.py register sdist --format=bztar,gztar,zip upload')
