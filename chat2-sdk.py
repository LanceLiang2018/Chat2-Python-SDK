import requests
import json
import base64
import threading
import time


class Chat2Comm:
    def __init__(self, server_choose=1):
        self.servers = ["https://lance-chatroom2.herokuapp.com/",
                        "http://127.0.0.1:5000/"]
        self.SERVER = self.servers[server_choose]
        self.MAIN = self.SERVER + ""
        self.ABOUT = self.SERVER + "about"
        self.BEAT = self.SERVER + "beat"
        self.LOGIN = self.SERVER + "login"
        self.SIGNUP = self.SERVER + "signup"
        self.GET_MESSAGE = self.SERVER + "get_message"
        self.GET_NEW_MESSAGE = self.SERVER + "get_new_message"
        self.SEND_MESSAGE = self.SERVER + "send_message"
        self.GET_HEAD = self.SERVER + "get_head"
        self.CLEAR_ALL = self.SERVER + "clear_all"
        self.SET_USER = self.SERVER + "set_user"
        self.JOIN_IN = self.SERVER + "join_in"
        self.CREATE_ROOM = self.SERVER + "create_room"
        self.SET_ROOM = self.SERVER + "set_room"
        self.GET_ROOMS = self.SERVER + "get_room_all"
        self.GET_ROOM_INFO = self.SERVER + "get_room_info"
        self.SET_ROOM_INFO = self.SERVER + "set_room_info"
        self.GET_MEMBERS = self.SERVER + "get_members"
        self.UPLOAD = self.SERVER + "upload"
        self.MAKE_FRIENDS = self.SERVER + "make_friends"

        self.UID = 'uid'
        self.MID = 'mid'
        self.GID = 'gid'
        self.AUTH = 'auth'
        self.MESSAGE_TYPE = 'message_type'
        self.USERNAME = 'username'
        self.PASSWORD = 'password'
        self.EMAIL = 'email'
        self.NAME = 'name'

    # 异步post请求
    def post_(self, url: str, params: dict, callback):
        def post_request(murl: str, mparams: dict, mcallback):
            mcallback(requests.post(murl, data=mparams))
        t = threading.Thread(target=post_request, args=(url, params, callback))
        # t.setDaemon(True)
        t.start()

    def post(self, url: str, params: dict):
        r = requests.post(url, data=params)
        if r.status_code != 200:
            return {'code': '-1', 'message': "Server Error."}
        return r.json()

    def get(self, url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return {'code': '-1', 'message': "Server Error."}
        return r.json()

    # 异步get请求
    def get_(self, url: str, callback):
        def post_request(murl: str, mcallback):
            mcallback(requests.get(murl))
        t = threading.Thread(target=post_request, args=(url, callback))
        # t.setDaemon(True)
        t.start()


class Chat2Client:
    def __init__(self, server_choose=1):
        self.comm = Chat2Comm(server_choose=server_choose)
        self.username = ""
        self.auth = ""
        self.gid = 0
        self.latest_mid = 0
        self.load()

    def init(self):
        self.username = ""
        self.auth = ""
        self.gid = 0
        self.latest_mid = 0
        self.save()

    def save(self):
        with open('save.json', 'w') as f:
            f.write(json.dumps({
                'username': self.username,
                'auth': self.auth,
                'latest_mid': self.latest_mid}))

    def load(self):
        try:
            with open('save.json', 'r') as f:
                settings = json.load(f)
                self.username = settings['username']
                self.auth = settings['auth']
                self.latest_mid = settings['latest_mid']
        except Exception as e:
            print(e)

    def parse_errors(self, result):
        print(result['message'])

    def post_auth(self, url: str, params: dict):
        params['auth'] = self.auth
        return self.comm.post(url, params)

    def login_(self, username, password):
        def login_callback(request):
            result = json.loads(request.text)
            if result['code'] != '0':
                self.parse_errors(result)
                return
            self.auth = result['data']['auth']
            self.username = username
        self.comm.post_(self.comm.LOGIN, {'username': username, 'password': password}, login_callback)

    def login(self, username, password):
        result = self.post_auth(self.comm.LOGIN, {'username': username, 'password': password})
        if result['code'] != '0':
            self.parse_errors(result)
            return
        self.username = username
        self.auth = result['data']['auth']

    def signup(self, username, password, email='LanceLiang2018@163.com', name='Lance'):
        result = self.post_auth(self.comm.SIGNUP,
                                {'username': username, 'password': password, 'email': email, 'name': name})
        if result['code'] != '0':
            self.parse_errors(result)
            return

    def logout(self):
        self.auth = ''

    def beat(self):
        result = self.post_auth(self.comm.GET_ROOMS, {})
        if result['code'] != '0':
            self.parse_errors(result)

    def create_room(self, room_name):
        result = self.post_auth(self.comm.CREATE_ROOM, {'name': room_name})
        if result['code'] != '0':
            self.parse_errors(result)

    def get_rooms(self):
        result = self.post_auth(self.comm.GET_ROOMS, {})
        if result['code'] != '0':
            self.parse_errors(result)
            return
        return result['data']['room_data']

    def enter_room(self, gid: int):
        self.gid = gid

    def get_new_message(self, gid: int=0):
        if gid == 0:
            gid = self.gid
        result = self.post_auth(self.comm.GET_NEW_MESSAGE, {'since': self.latest_mid, 'gid': gid})
        if result['code'] != '0':
            self.parse_errors(result)
            return
        messages = result['data']['message']
        for m in messages:
            self.latest_mid = max(self.latest_mid, m['mid'])
        self.save()
        return messages

    def send_message(self, text: str, message_type='text', gid=0):
        if gid == 0:
            gid = self.gid
        result = self.post_auth(self.comm.SEND_MESSAGE,
                                {'message_type': message_type, 'text': text, 'gid': gid})
        if result['code'] != '0':
            self.parse_errors(result)
            return

    def upload(self, filename, data):
        result = self.post_auth(self.comm.UPLOAD, {'data': data, 'filename': filename})
        if result['code'] != '0':
            self.parse_errors(result)
            return
        return result['data']['upload_result']

    def clear_all(self):
        result = self.post_auth(self.comm.CLEAR_ALL, {})
        print('Clear_ALL:', result)
        return

    def make_friends(self, friend: str):
        result = self.post_auth(self.comm.MAKE_FRIENDS, {'friend': friend})
        if result['code'] != '0':
            self.parse_errors(result)
            return

    def join_in(self, gid: int):
        result = self.post_auth(self.comm.JOIN_IN, {'gid': str(gid)})


def module_test():
    client = Chat2Client(server_choose=0)
    client.init()
    client.clear_all()
    client.signup('Lance', '')
    client.login('Lance', '')
    # time.sleep(1)
    print(client.username, client.auth)
    client.create_room('NameLose')
    rooms = client.get_rooms()
    print(rooms)
    client.enter_room(rooms[0]['gid'])
    messages = client.get_new_message()
    print(len(messages), messages)
    messages = client.get_new_message()
    print(len(messages), messages)
    client.send_message('First commit~')
    messages = client.get_new_message()
    print(len(messages), messages)

    with open('save.json', 'rb') as f:
        data = f.read()
        b64 = base64.b64encode(data)
        upload_result = client.upload('save.json', b64)
        print(upload_result)

    client.send_message(upload_result['url'], message_type='file')
    messages = client.get_new_message()
    print(len(messages), messages)


def mini_test():
    client = Chat2Client()
    client.login('Lance', '')
    print(client.username, client.auth)
    rooms = client.get_rooms()
    print(rooms)
    client.enter_room(rooms[0]['gid'])

    while True:
        messages = client.get_new_message()
        print(len(messages), messages)
        for m in messages:
            client.send_message('我反对 @%s的观点！' % m['username'])
            client.latest_mid = client.latest_mid + 1
            client.save()
        time.sleep(10)


def friend_test():
    client = Chat2Client(server_choose=0)
    client.login('Lance', '')
    rooms = client.get_rooms()
    print(rooms)
    client.join_in(2)
    # client.make_friends('Tony')
    # rooms = client.get_rooms()
    # print(rooms)
    client.enter_room(3)
    while True:
        messages = client.get_new_message()
        print(len(messages), messages)
        for m in messages:
            client.send_message('我在听~ @%s\n你说%s' % (m['username'], m['text']))
            client.latest_mid = client.latest_mid + 1
            client.save()
        time.sleep(3)


if __name__ == '__main__':
    # module_test()
    # mini_test()
    friend_test()