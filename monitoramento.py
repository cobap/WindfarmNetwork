"""."""

import socket
import sys
from threading import Thread
import random

class Monitoramento:

    def __init__(self, host, port, numero_turbinas):
        self.host = host
        self.port = port
        self.numero_turbinas = numero_turbinas
        self.velocidade_vento = random.random() * 10 + 1
        self.turbinas_online = []
        self.turbinas_falha = []

    # Inicia servidor
    def start_server(self):
        # Cria novo socket utilizando IPv4 e TCP
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Tentamos fazer bind a porta - caso esta esteja ocupada, irá falhar e o programa ira fechar
        try:
            soc.bind((self.host, self.port))
        except:
            print("Erro ao fazer 'bind' na porta: " + str(sys.exc_info()))
            sys.exit()

        # Caso o bind seja um sucesso, abrimos para uma fila de ate 5 conexoes
        soc.listen(self.numero_turbinas)

        print("-- Iniciando monitoramento --")

        # Iniciamos um loop inifito, sempre aceitando novas conexoes
        while True:
            # Aceita a nova conexao do cliente
            connection, address = soc.accept()
            # Identificamos qual o IP e a PORTA que o cliente se encontra
            ip, port = str(address[0]), str(address[1])
            print("Nova turbina conectada: " + ip + ":" + port)

            # Para essa nova conexao, iniciamos uma nova thread, e passamos como argumento os detalhes da conexao (socket do cliente), IP e a PORTA
            try:
                Thread(target=self.client_thread, args=(connection, ip, port)).start()
            except:
                print("Aconteceu algum erro ao criar a Thread")
                print(str(sys.exc_info()))

        # Por ultimo fechamos o socket do pai
        soc.close()

    # Thread que ira cuidar de toda conexao de um novo cliente
    def client_thread(self, connection, ip, port, max_buffer_size = 5120):
        # Bool que define se cliente ainda esta conectado
        is_active = True

        # Mantemos a conexao enquanto o cliente estiver ativo (recebendo pacotes ou nao saiu da aplicacao)
        while is_active:
            # Recebemos o input do cliente com no maximo 5120 Bytes
            client_input = self.receive_input(connection, max_buffer_size)

            # Se o cliente enviar um quit, fechamos o socket (connection) e colocamos o cliente como ativo=Falso
            if "--QUIT--" in client_input:
                print("Cliente " + ip + ":" + port + " esta cancelando a conexao")
                connection.close()
                is_active = False
            else:
                print("Turbina {0} conectada com status {1}".format(client_input[:5], client_input[-1]))

                #TODO
                if client_input == 'EGG':
                    connection.sendall("easter".encode("utf8"))
                else:
                    connection.sendall("--".encode("utf8"))

    # Recupera o input do cliente
    def receive_input(self, connection, max_buffer_size):
        # Recupera do buffer ate 5012 Bytes do cliente
        client_input = connection.recv(max_buffer_size)
        # Mede o tamanho do input do cliente - dos 5012 permitidos
        client_input_size = sys.getsizeof(client_input)

        print("Cliente enviou mensagem de " + str(sys.getsizeof(client_input)) + " BYTES")

        # Caso envie um tamanho maior que o size, mandamos esse print
        if client_input_size > max_buffer_size:
            print("The input size is greater than expected {}".format(client_input_size))

        # Decode and strip end of line
        decoded_input = client_input.decode("utf8").rstrip()
        return str(decoded_input).upper()


    def process_input(self, input_str):
        print("Processing the input received from client")

if __name__ == "__main__":
    monitoramento = Monitoramento('127.0.0.1', 5123, 5)
    monitoramento.start_server()
