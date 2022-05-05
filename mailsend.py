from socket import *
import json

class mailSend():
	def __init__(self, jsonFile, title, msg):
		with open(jsonFile, "r", encoding='utf-8') as f:
			info = json.load(f)
		assert 'student_id' in info, "student_id not found"
		self.FROM = "897755101@qq.com"
		self.TO = info['student_id'] + "@smail.nju.edu.cn"
		self.username = "ODk3NzU1MTAxQHFxLmNvbQ=="
		self.password = "dGFzeWd5dGlqd3JpYmNqYg=="
		self.title = title
		self.msg = msg
		self.endmsg = "\r\n.\r\n"
		self.mailserver = ("smtp.qq.com", 25)

	def sendMsg(self):
		clientSocket = socket(AF_INET, SOCK_STREAM)
		clientSocket.connect(self.mailserver)

		recv = clientSocket.recv(1024).decode()
		if recv[:3] != '220':
			print('220 reply not received from server.')
			clientSocket.close()
			return False

		heloCommand = 'HELO NJUHealthCheckin\r\n'
		clientSocket.send(heloCommand.encode())
		recv1 = clientSocket.recv(1024).decode()
		if recv1[:3] != '250':
			print('250 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send('AUTH LOGIN\r\n'.encode())
		recv2 = clientSocket.recv(1024).decode()
		if recv2[:3] != '334':
			print('334 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send((self.username + '\r\n').encode())
		recv3 = clientSocket.recv(1024).decode()
		if recv3[:3] != '334':
			print('334 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send((self.password + '\r\n').encode())
		recv4 = clientSocket.recv(1024).decode()
		if recv4[:3] != '235':
			print('235 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send(('MAIL FROM:<' + self.FROM + '>\r\n').encode())
		recv5 = clientSocket.recv(1024).decode()
		if recv5[:3] != '250':
			print('250 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send(('RCPT TO:<' + self.TO + '>\r\n').encode())
		recv6 = clientSocket.recv(1024).decode()
		if recv6[:3] != '250':
			print('250 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send('DATA\r\n'.encode())
		recv7 = clientSocket.recv(1024).decode()
		if recv7[:3] != '354':
			print('354 reply not received from server.')
			clientSocket.close()
			return False

		clientSocket.send(('From: NJUHealthCheckin Project\r\n').encode())
		clientSocket.send(('To: ' + self.TO + '\r\n').encode())
		clientSocket.send(('Subject: ' + self.title + '\r\n').encode())
		clientSocket.send(self.msg.encode())

		clientSocket.send(self.endmsg.encode())

		clientSocket.send('QUIT\r\n'.encode())
		recv8 = clientSocket.recv(1024).decode()
		if recv8[:3] != '250':
			print('250 reply not received from server.')
			clientSocket.close()
			return False
		clientSocket.close()
		return True

if __name__ == '__main__':
	mail = mailSend("myconfig.json", "测试", "abc")
	mail.sendMsg()