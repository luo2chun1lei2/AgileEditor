Starter of Agile Editor

1, 用于配置Gtk的全局快捷键，启动特定的程序。
2, 一旦得到信号，就发送给其他程序。
    因为其他程序都采用gi.repository模型，和pygtk不兼容，只能通过信号传递。
