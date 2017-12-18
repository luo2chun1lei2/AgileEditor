# -*- coding:utf-8 -*-

'''
记录检索的历史的控件。
'''
import logging
from gi.repository import Gtk
from framework.FwManager import FwManager
from framework.FwComponent import FwComponent

class ViewSearchHistory(FwComponent):
    def __init__(self):
        super(ViewSearchHistory, self).__init__()
        
        self._init_view()
        self.invoked = False
        
    # from FwBaseComponnet
    def onRegistered(self, manager):
        info = [{'name':'view.search_history.get_view', 'help':'get the view of search history.'},
                {'name':'view.search_history.set_model', 'help':'set search history list.'},
                {'name':'view.search_history.push', 'help':'push search action into queue.'},
                {'name':'view.search_history.pop', 'help':'pop search action into queue.'}]
        manager.register_service(info, self)

        manager.register_event_listener('model.search_history.changed', self)

        return True
    
    # override component
    def onSetup(self, manager):
        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchPushHistory',
                  'title':"Add Search History",
                  'accel':"",
                  'stock_id':Gtk.STOCK_GO_FORWARD,
                  'service_name': 'ctrl.search_history.push'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchPopHistory',
                  'title':"Restore Search History",
                  'accel':"",
                  'stock_id':Gtk.STOCK_GO_BACK,
                  'service_name': 'ctrl.search_history.pop'}
        manager.request_service("view.menu.add", params)
        
        params = {'view':self.view}
        manager.request_service("view.menu.add_toolbar", params)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.search_history.get_view":
            return (True, {'view': self.view})
        else:
            return False, None

    # override FwListener
    def on_listened(self, event_name, params):
        if event_name == 'model.search_history.changed':
            self.actions = params['list']
            
            model = self.view.get_model()
            model.clear()
            for a in self.actions:
                model.append(['%s : %s' % (a['action_id'], a['text'])])
                
            self.invoked = True
            self.view.set_active(0)
        else:
            return False

    def _init_view(self):
        ''' 这里创建combobox，列表是检索动作数组。 
        '''
        self.view = Gtk.ComboBox.new()
        
        cell_render = Gtk.CellRendererText.new()
        self.view.pack_start(cell_render, True)
        self.view.add_attribute(cell_render, "text", 0)
        
        list = Gtk.ListStore(str)
        self.view.set_model(list)
        
        self.view.set_active(0)
        
        self.view.connect("changed", self._on_row_changed)
        
    def _on_row_changed(self, view):
        if self.invoked:    # 被代码调用产生的事件。
            self.invoked = False
            return
        
        selected_index = view.get_active()
        if selected_index == -1:    # 没有选中的项目
            return

        logging.debug('selected %d' % selected_index)
        action = self.actions[selected_index]
        FwManager.instance().request_service('ctrl.search_history.do_action',
                    {'action_id':action['action_id'], 'text': action['text']})
        