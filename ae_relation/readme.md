Agile Relation Editor

安装：
pip install prompt_toolkit

目标：
  用特定的语法描述元素和它们之间的关系，然后可以显示和编辑。
  
设计方案：
1. 元素(element)是此程序中所有的对象的统称。
1. 关系(relation)是元素之间的关系，实例必须关联两个以上对象。
1. 属性(property)是依附于某个元素的元素，关系是“属性”。
  当属性依附的元素消失时，则属性消失。
  
安装
pip install CodernityDB
这个是 Python 语言开发的，嵌入到程序中的NoSQL DB，是 key-value 类型。
   
具体的实现：
1. 设计成为两层，最外层是 Control-Model。
    1. Control：是控制整个System和Model的。
    1. Model:整个系统的模型，包含下面的所有的模块。
1. Model：
    1. Data是基本的数据结构，包含Element和Relation。
        1. External Data，是建立在基础数据结构上的扩展数据结构。
           目前实现的UMLClass之类的就是。
        1. Storage，是将Data保存起来的模块。它不需要知道每个Data的具体含义，
           但是需要可以遍历和保存基础的单元。
        1. Display，是将Data表现出来的模块，不许需要知道每个Data的具体含义，
           但是需要可以遍历和显示基础的单元。
           怎么显示单元和遍历，则是display policy设置的。
1. Control，是对Data、Storage、Display的控制，
   总之是针对整个系统的控制。

要点：   
1. 设计成以上结构，是方便替换实现方法，但是会需要程序设计的非常精巧，这个尽量采用简单的实现方案吧。
