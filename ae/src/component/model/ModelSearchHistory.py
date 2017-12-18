# -*- coding:utf-8 -*-
'''
检索动作列表。
'''
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ModelSearchHistory(FwComponent):
    def __init__(self):
        super(ModelSearchHistory, self).__init__()

        # 记录 = [SearchAction]
        self.search_actions = []
        self.current_index = -1
        
    # override component
    def onRegistered(self, manager):
        info = [{'name':'model.search_history.push', 'help':'push one search action into history.'},
                {'name':'model.search_history.pop', 'help':'pop one search action from history.'},
                {'name':'model.search_history.get_list', 'help':'get list of search actions.'},
                {'name':'model.search_history.get_action', 'help':'get one action in list of search actions.'}]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "model.search_history.push":
            self._push(params)
            return (True, None)
        elif serviceName == 'model.search_history.pop':
            action = self._pop(params)
            return (True, {'action_id': action.action_id, 'text': action.text})
        elif serviceName == 'model.search_history.get_list':
            return (True, {'list':self.search_actions()})
        elif serviceName == 'model.search_history.active_action':
            self.current_index = params['index']
            return (True, {'action': self.search_actions()[self.current_index]})
        else:
            return (False, None)

    def _push(self, params):
        self.search_actions.insert(0, {'action_id':params['action_id'], 'text':params['text']})
        
        FwManager.instance().send_event('model.search_history.changed', {'list': self.search_actions})
        
    def _pop(self, action):
        action = self.search_actions.pop()
        
        return action
