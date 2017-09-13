环境要求：
1，需要安装Python 2.6，用于Python语言。
2，需要安装PyGObject，用于使用Gnome控件（适用于Gnome 3.0）。
3，eclipse 4.4（Java开发环境），再安装PyDev。
4，需要安装id-utils，这部分实际上没有仔细的运行。
5, 请执行install_dev.sh

参考：
1, Python GI API Reference:
    http://lazka.github.io/pgi-docs/
2, 本机代码参考：
    /usr/lib/python2.7/dist-packages/gi

3, gtk source view的语言分析
/usr/share/gtksourceview-2.0/language-specs

4，修改global的配置文件，加入需要避免的路径。
cp ./doc/global/examples/gtags.conf etc/
在common::skip中加入obj/

Plat:
2017/9/9 ～ ？
开始进入结构调整期，在增加新的功能时，发现开发非常的不方便，应该将函数和模块的调用方法不断的剥离成
1，有一个主体结构，但是此结构下没有具体的功能。
1.1 主体结构以注册和消息分发机制为核心。
1.2 画面不是组合的，而是基于请求的，请求什么样的画面服务，就显示什么样的画面。
2，在此主体结构上，添加功能模块，称为组件。功能模块之间保持彼此之间的独立性。
2.1 组件之间不可见，而是通过发送消息的方式来处理。
2.2 组件可以分为画面、处理、数据和控制。
2.3 需要建立组件之间的依赖关系，需要保证组件之间的加载顺序。
3，实现：容易添加新的模块、修改模块内部的实现而不影响其他模块。
4，为以后扩展新的代码分析和界面处理而做准备。

框架怎么设计？
-----------
比如现在有 data是File/Project/ProjectList，
然后画面有Tree/List/InfomationDialog 等。
最后，控制有 new（创建信息的模型或者画面）、delete（销毁信息模型或画面）、change（修改信息模型或者画面）、link（将两个对象相互关联，一个改变后，另外一个也跟着改变）。