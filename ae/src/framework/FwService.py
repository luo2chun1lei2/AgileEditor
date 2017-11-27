#-*- coding:utf-8 -*-
'''
提供Service功能。
'''
import sys, logging

from FwUtils import *

class FwService(object):
    ''' 服务提供者
    '''
    def __init__(self):
        pass

class _FwServiceItem(object):
    ''' 保存Service的信息和提供服务的组件。
    '''
    def __init__(self, info, FwService):
        self.info = info
        self.service = FwService

class FwServiceCenter(object):
    ''' 服务中心，允许FwService可以注册服务、调用服务等。
    '''
    
    def __init__(self):
        # [服务的信息]: [<_FwServiceItem>]
        super(FwServiceCenter, self).__init__()
        
        self.services = []
    
    #################################################
    # 服务参数必须包括
    # "name": string: 服务的标志名字，建议用“xx.xx” 来表示。
    #    如果名字匹配，就会调用此组件。
    # "help": string: 显示帮助信息。

    def register_service(self, info, component):
        ''' 注册服务，允许同一个服务名字被多个组件注册。
        @param info: map/[map]: 服务的关键字加参数。
        @param service: FwComponent: 组件实例
        '''

        if isinstance(info, list):
            for i in info:
                if self._has_registered(i['name']):
                    logging.error("There is service name '%s'." % i['name'])
                    sys.exit(1)
                self.services.append(_FwServiceItem(i, component))
        else:
            if self._has_registered(info['name']):
                logging.error("There is service name '%s'." % info['name'])
                sys.exit(1)
            self.services.append(_FwServiceItem(info, component))
        return True

    def _has_registered(self, service_name):
        ''' 目前service不能同名。TODO 这里发现有问题，但是没有时间研究发生了什么！'''
#         for s in self.services:
#             if s.info['name'] == service_name:
#                 return True
#         return False
        return False

    def unregister_service(self, component):
        ''' 注销一个组件的所有服务。
        @param service: FwComponent: 组件实例
        '''
        for service in self.services:
            if service.service is component:
                index = service.services.index(component)
                del self.services[index]
        return True

    def request_service(self, serviceName, params=None):
        ''' 请求服务
        @param serviceName: string: 服务名称，必须和service的info的name相同。
        @param params: map: 传递给应答的组件
        @return (bool, map): (请求是否成功，返回数据) 
        '''
        for service in self.services:
            if service.info['name'] == serviceName:
                return service.service.onRequested(self, serviceName, params)

        # 也不一定是错误，可能是因为初始化顺序导致的。
        logging.warn("cannot find service \"%s\"." % serviceName)
        util_print_frame()
        return (False, None)

