from chat2_sdk import Chat2Client

if __name__ == '__main__':
    client = Chat2Client(server_choose=0)
    client.login('Lance', '')
    client.enter_room(4)
    client.send_message('TEST 测试')