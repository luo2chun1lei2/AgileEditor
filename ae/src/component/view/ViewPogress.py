# -*- coding:utf-8 -*-
'''
显示在后台进行的任务的进度。
'''
from gi.repository import Gtk
from framework.FwManager import FwManager
from framework.FwComponent import FwComponent

class ViewProgress(FwComponent):
    def __init__(self):
        super(ViewProgress, self).__init__()

        self._init_view()

    # from FwBaseComponnet
    def onRegistered(self, manager):
        manager.register_event_listener('task.progress.start', self)
        manager.register_event_listener('task.progress.stop', self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        return False, None

    # override FwListener
    def on_listened(self, event_name, params):
        if event_name == 'task.progress.start':
            self.view.start()
        elif event_name == 'task.progress.stop':
            self.view.stop()
            return True
        else:
            return False

    # override component
    def onSetup(self, manager):
        # Add tool item.
        params = {'view':self.view}
        manager.request_service("view.menu.add_toolbar", params)

        return True

    def _init_view(self):
        ''' 这里使用spinner，是因为无法预料时间。如果可以预料，可以用 progress bar。 
        '''
        self.view = Gtk.Spinner.new()
