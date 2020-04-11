# arcaea-mp

一个可以实现简单的 Arcaea 多人游戏的库

使用了 Arcaea Score Prober 的 API 来查询分数。

## 工作原理

- `Listener` 设置一个循环。这个循环用来检查房间列表里所有的房间，并在需要时将其结算。Listener 通过操作相对应房间的方法来更新房间数据。
- `Multiplayer` 类描述了一个房间。它记录着每一局的游戏情况，包括分数和玩家排名。

## 依赖

- `brotli` mdoule
- `websockets` module

## 使用

使用 git 克隆仓库到项目文件夹。

```shell script
git clone -u arcaea https://github.com/Cyanoxygen/arcaea-mp
cd arcaea
mv config.example.py config.py
```
然后编辑 `config.py`，指定查询间隔（默认 200s ）。
之后你就可以将其用于你的程序：
```python
from arcaea import *
listener = Listener()

# 为了在结算后及时获取动态，定义一个函数
def onScoreComplete(mp):
    pass

# 创建一个房间：
listener.addmp('ident', 'host_user_code', 'title', members=10)

# 然后注册刚才定义的函数到房间：
listener.mplist['ident'].regcall('onScoreComplete', onScoreComplete)

# 然后使用 mplist 成员对所需房间进行操作
listener.mplist['ident'].set_song('song', 'diff')

# 开始下一轮 PK
listener.mplist['ident'].nextround()

# 在指定的间隔之后房间自动结算并执行相应的函数（如果已经注册了）
```

## 结构
Listener 类负责监测所有可管理的房间。一旦有房间的本局游戏开始时间距现在超过设定的间隔，Listener 就会自动结束本局游戏。

Multiplayer 类描述一个房间，具有一些方法，比如设置本轮游戏的歌曲等。

Score 描述一个成绩。

- `class MultiplayerListener`

    监听器，使用线程监听，有一个主循环。
    - `.start()`
    
      启动当前的监听器实例。
     
    - `.addmp(ident: str, host: str, title='Arcaea Multiplayer', members=10`

        向当前实例内添加一个房间。
        - `ident`: 字符串，用作唯一识别
        - `host`: 字符串，9 位数的 Arcaea Usercode
        - `title`: 字符串，房间名
        - `members`: 整数，房间最大人数
        
- `class Multiplayer` 
    
    描述一个房间。
    
    - `Multiplayer(ident, host, title, members=10)`
    
        创建一个 Multiplayer 实例。如果配合 Listener 使用，请使用 `Listener.addmp()`。
        
        - `ident`: 字符串，用作唯一识别
        - `host`: 字符串，9 位数的 Arcaea Usercode
        - `title`: 字符串，房间名
        - `members`: 整数，房间最大人数
        
    - `.regcall(type, callback)`
    
        有时配合 Listener 使用时你无法在房间状态发生改变时及时响应。这里提供一个 Call 机制，让你可以在房间发生状态改变时调用相应的方法。
        一共有 5 个函数可供调用：
         - `onRemove` ：当有用户从房间中移出时所调用的函数。
         - `onStop` ：当房间的某一轮停止时所调用的函数。
         - `onScoreComplete` ：在房间的某一轮结算完成后所调用的函数。
         - `onClosed` ：在房间关闭后所调用的函数。
         
         - `type` ：字符串，调用函数的类型。
         - `callback` ：函数标识符。要调用的函数。
        
    - `.add_member(usercode)`
        
        向当前房间添加一个用户。
        - `usercode` ：字符串，Arcaea 9 位数 ID
        
    - `.rm_member(usercode, reason)`
    
        从当前房间移出一个用户。
        - `usercode` ：字符串，Arcaea 9 位数 ID
        - `reason`：字符串，移出用户的原因。
        
    - `.set_song(songid, diff)`
    
        设置当前局的谱面。
        - `songid`  ：字符串，歌曲 ID
        - `diff`    ：字符串，难度（`pst`, `prs`, `ftr`）之一）。
        
    - `.nextround()`
    
        开始本轮游戏。
        
    - `stop()`
    
        停止本轮游戏。
       