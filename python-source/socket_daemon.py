#!/usr/bin/python

import socket
import sys
import cv2
import numpy as np
from _thread import *
from threading import Thread


class TcpClientTest:
    def __init__(self, image_path):

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ''
        port = 12334

        print('Waiting for connection')
        try:
            client_socket.connect((host, port))
        except socket.error as e:
            print(str(e))
            return

        image_test = cv2.imread(image_path)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', image_test, encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()

        while True:
            cv2.imshow('Client', image_test)
            cv2.waitKey(1000)
            try:
                client_socket.sendall(str('L83F').encode('utf-8'))
                client_socket.sendall(str(len(stringData)).ljust(16).encode('utf-8'))
                client_socket.sendall(stringData)
                response = client_socket.recv(2048)
                print(response.decode('utf-8'))
            except socket.error as e:
                print(str(e))


class ClientHandlerThread(Thread):
    def __init__(self, connection):
        Thread.__init__(self)
        self.connection = connection
        self.running = True

    def recvall(self,connection, count):
        buf = b''
        while count:
            new_buffer = connection.recv(count)
            if not new_buffer:
                return None
            buf += new_buffer
            print(len(new_buffer))
            count -= len(new_buffer)

        return buf

    def terminate(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                magic_id = self.connection.recv(4)
                if not magic_id:
                    continue

                if magic_id.decode('utf-8') != 'L83F':
                    print("Client sent a strange msg, something wrong...: {}".format(magic_id.decode('utf-8')))
                    continue

                data_header = self.connection.recv(16)
                image_size = int(data_header.decode('utf-8'))

                print("Client sent a image with: {} (bytes)".format(image_size))
                buffer = self.recvall(self.connection, image_size)
                np_encoded_img = np.fromstring(buffer, dtype='uint8')
                decoded_img = cv2.imdecode(np_encoded_img, 1)
                cv2.imshow('SERVER', decoded_img)
                cv2.waitKey(100)
                self.connection.sendall(str.encode('thank you'))
            except KeyboardInterrupt:  # exit from the client
                break
            except socket.timeout:
                pass

        self.connection.close()
        print("connection with client closed)")

class TcpServer:
    def __init__(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host = ''
        port = 12334

        try:
            server_socket.bind((host, port))
        except socket.error as e:
            print(str(e))

        print('Waiting for a Connection.. on {}:{}'.format(host, port))
        server_socket.listen(5)
        server_socket.settimeout(1.0)

        def recvall(connection, count):
            buf = b''
            while count:
                new_buffer = connection.recv(count)
                if not new_buffer:
                    return None
                buf += new_buffer
                print(len(new_buffer))
                count -= len(new_buffer)

            return buf

        current_client_thread = None
        thread_count = 0

        while True:
            try:
                client_conn, address = server_socket.accept()
                if client_conn:
                    if current_client_thread:
                        print('Terminating previous connection - ' + 'Connection Number: ' + str(thread_count))
                        current_client_thread.terminate()
                        current_client_thread.join()
                        print('Terminated previous connection')
                    print('Connected to: ' + address[0] + ':' + str(address[1]))
                    current_client_thread = ClientHandlerThread(client_conn)
                    current_client_thread.start()
                    thread_count += 1
                    print('Connection Number: ' + str(thread_count))
            except socket.timeout:
                pass
            except KeyboardInterrupt: # exit from the server
                current_client_thread.terminate()
                current_client_thread.join(100)
                server_socket.close()
                print("socket closed")
                break
            except:
                raise


if __name__ == '__main__':
    print('Argument List:', str(sys.argv))
    if sys.argv[1] == 'server':
        TcpServer()
    if sys.argv[1] == 'client':
        TcpClientTest('/home/lucas/Downloads/20190919_094700s.jpg')
