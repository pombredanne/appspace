'''tubing application namespace management'''

from zope.component.registry import Components #@UnresolvedImport
from zope.interface import implements as appifies #@UnresolvedImport
from zope.interface.interface import InterfaceClass as AppSpacer #@UnresolvedImport

from tubing.util import reify

AppSpaceKey = AppSpacer('AppSpaceKey')


class AApp(AppSpaceKey):
    pass


class AAppSpace(AppSpaceKey):

    def getapp(): #@NoSelf
        pass

    def askapp(): #@NoSelf
        pass

    def setapp(): #@NoSelf
        pass

    def deleteapp(): #@NoSelf
        pass


class AppSpace(Components):

    appifies(AAppSpace)

    @reify
    def getapp(self):
        return self.getUtility

    @reify
    def askapp(self):
        return self.queryUtility

    @reify
    def setapp(self):
        return self.registerUtility

    @reify
    def deleteapp(self):
        return self.unregisterUtility


global_appspace = AppSpace('global')