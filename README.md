Chatroom System
    By Su ZX
=============================================
一、运行环境

Python 3.x

二、运行方法

python server.py
python client.py

三、网络配置

HOST = 127.0.0.1   # 服务器的IP地址
POST = 8998        # 服务器使用的端口

已在代码中完成配置，无需额外操作。

四、文件目录

Chatroom
├── forms
|   ├── __init__.py
|   ├── login_form.py
|   └── chat_form.py
├── server.py
├── client.py
├── server_memory.py
├── client_memory.py
├── message.py
└── README.md

五、功能简介
    
    1.登录系统

    成功运行客户端后，会出现登录界面。
    输入要在聊天室中使用的Nickname，单击Sign in按钮。
    若输入为空，弹出提示"Nickname cannot be empty."；若输入的Nickname已被使用，则弹出提示"This nickname has been used."。这两种情况下均无法登入聊天室，需重新输入合法的Nickname。
    当输入的Nickname合法时，登录界面关闭，进入聊天界面。

    2.在线聊天

    本聊天室系统用于所有用户一同进行的多人实时聊天，每个人发出的消息都将被全部当前在线用户接收和阅读。
    聊天界面的窗口可以自由缩放，其分为上下两部分，上方为显示窗口，用于显示所有用户发出的实时消息，下方为输入窗口，用于当前用户输入和发送消息。
    
    ------------------------------ 显示窗口 -----------------------------
    所有消息都会与其发送时间一同显示，时间格式为“年-月-日 时-分-秒”。
    有新消息时，显示窗口会自动滚动到底部确保新消息及时得到显示。
    而对于不同来源的消息，显示窗口采用了不同的显示样式以便于区分和阅读：
    【服务器发出的系统消息】
        发送时间与消息内容分两行用灰色小字体居中显示。
    【当前用户自己发出的消息】
        发送者的Nickname与发送时间在同一行用绿色字显示，下一行用黑色字显示消息内容，统一居左。
    【其他用户发出的消息】
        发送者的Nickname与发送时间在同一行用蓝色字显示，同样在下一行用黑色字显示消息内容，统一居左。
    
    ------------------------------ 输入窗口 -----------------------------
    在输入窗口中输入消息内容，单击右下角Sent Message按钮（或Ctrl+Enter）将消息发出。
    消息内容为空时，无法发出消息。
    键盘上的Enter回车键用于输入消息时换行，Ctrl+Enter组合键可直接发出消息。

六、协议设计
    
    该协议用于在聊天室系统的客户端和服务器端间进行有效通信。

    1.具体格式
    
    协议决定了客户端与服务器相互发送的报文格式。为了便于使用和实现，在格式上没有对请求报文和响应报文进行区分。
    具体报文分为两层：
    【第一层】
        |--Sender(4 Bytes)--|--MessageType(1 Byte)--|--Message--|
        a) 4字节的Sender字段，储存了该报文发送方的socket对象套接字的文件描述符。
           注：为了便于识别和操作，当发送方为服务器时，Sender字段设置为0。
        b) 1字节长的MessageType字段，储存了报文的功能类型。
        c) 报文消息字段Message，其内部进一步分出如下的第二层。
    【第二层】
        |--BodyType(1 Byte)--|--BodyLen--|--Body--|
        a) 1字节长的BodyType字段，储存了报文主体的数据类型。
        b) BodyLen字段，储存了报文主体的长度。
        c) 报文主体字段，真正存储了客户端和服务器端之间通信时发送的原始消息。

    2.报文功能类型字段
    
    MessageType字段的值表示了该报文的具体功能，已实现的功能及其对应值如下：
        connect_request = 1   # 客户端发送用于测试连接情况的信息
        connect_confirm = 2   # 服务器通过了客户端对连接的测试，回复成功信息
        connect_refuse = 3    # 服务器未通过客户端对连接的测试，回复失败信息
        login_info = 4        # 客户端发送用于登录的信息
        login_confirm = 5     # 登录信息合法，服务器回复成功信息
        login_refuse = 6      # 登录信息不合法，服务器回复失败信息
        chat_message = 10     # 聊天消息的发送和转发
        name_request = 20     # 客户端发送socket对象套接字的文件描述符，请求其对应的用户信息
        name_info = 21        # 服务器回复用户信息
    增加功能时，可直接向其中添加新的字段值，实现方便且结构清晰。
    
    3.报文主体数据类型字段
    
    BodyType字段的值表示了该报文主体的数据类型，已实现的数据类型及其对应值如下：
            'str': 1
            'int': 2
    当前聊天室完整功能的实现仅需要字符串和整型这两种数据类型作为报文主体。
    后续增加功能时，若需要更丰富的数据类型，同样可直接向其中添加新的字段值。