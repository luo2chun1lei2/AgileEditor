# -*- coding:utf-8 -*-
'''
控制台。
'''
from gi.repository import Gtk, GLib, Pango, Vte

from framework.FwComponent import FwComponent

class ViewTerminal(FwComponent):
    def __init__(self):
        super(ViewTerminal, self).__init__()
        
        self._create_view()
    
    # override component
    def onRegistered(self, manager):
        info = [{'name':'view.terminal.get_view', 'help':'get view of ternimal.'},
                {'name':'view.terminal.init', 'help':'initialize the terminal.'}]
        manager.register_service(info, self)

        return True
    
    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.terminal.get_view":
            return (True, {'view': self._get_view()})
        
        elif serviceName == "view.terminal.init":
            self._init_ternimal(params['dir'])
            return (True, None)

        else:
            return (False, None)
    
    def _create_view(self):
        # 控制台
        self.terminal = Vte.Terminal()
        # self.terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.SYSTEM) # 2.90
        self.terminal.set_font(Pango.FontDescription.from_string("Ubuntu mono 12"))
        # self.terminal.set_scrollback_lines(True) 设置则没有滚动条。
        self.terminal.set_audible_bell(False)
        # self.terminal.set_input_enabled(True)    # 2.90
        self.terminal.set_scroll_on_output(True)

        self.scrl_terminal = Gtk.ScrolledWindow()
        self.scrl_terminal.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scrl_terminal.set_hexpand(True)
        self.scrl_terminal.set_vexpand(True)
        self.scrl_terminal.add(self.terminal)
    
    def _get_view(self):
        return self.scrl_terminal
    
    def _init_ternimal(self, dir_path):
        if hasattr(self.terminal, "spawn_sync"):  # 2.91
            self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,  # default is fine
                dir_path,
                ["/bin/bash"],  # where is the emulator?
                [],  # it's ok to leave this list empty
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,  # at least None is required
                None,
                )
        else:  # < 2.90
            self.terminal.fork_command_full(
                Vte.PtyFlags.DEFAULT,  # default is fine
                dir_path,
                ["/bin/bash"],  # where is the emulator?
                [],  # it's ok to leave this list empty
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,  # at least None is required
                None,
                )
