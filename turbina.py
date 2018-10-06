"""."""

import socket
import sys
import math
import time

class Turbina:
    """
        ID: identificador unico de uma turbina

        STATUS: representa o 'modo' com que a turbina se encontra
            0 - desligada
            1 - online
            2 - parada
            3 - com falha

        ALARME: contador de alarmes da turbina. +3 alarmes a turbina entra em "falha"

        PRODUCAO: calcula através de alguns fatores qual a producao atual da turbina em um tempo T
    """

    # Ja iniciamos uma nova turbina com o IP e PORTA do monitoramento + o ID dessa turbina
    def __init__(self, id, host, port):
        self.id = id
        self.status = 0
        self.host = host
        self.port = port

        # Enviamos uma mensagem tipo 0, para que o monitoramento registre essa turbina em sua lista
        self.envia_mensagem(0)

    def atualiza_turbina(self, vento_atual, tempo):
        self.fator_transformacao = vento_atual/(self.alarmes + 1)
        self.calcula_producao(self.fator_absorcao, self.fator_transformacao, tempo)

    def calcula_producao(self, fator_absorcao, fator_transformacao, tempo):
        """
        Producao de energia:
            fator_absorcao: o quanto a maquina consegue transformar de cinetica em mecanica
            fator_transformacao: o quanto a maquina consegue transformar de mecanica em eletrica
        """

        # Usamos a funcao consseno para não criar algo constante (vai variar conforme o tempo)
        # Quanto maior os fatores, mais energia é gerada
        energia_gerada = (math.cos(tempo) + 1) * fator_absorcao + fator_transformacao
        # print('COSSENO: ' + str(math.cos(tempo) + 1))
        # print('COM ABSORCAO: ' + str((math.cos(tempo) + 1) * fator_absorcao))
        # print('COM TRANSFORMACAO: ' + str((math.cos(tempo) + 1) * fator_absorcao + fator_transformacao))
        # print('PRODUCAO: ' + str(energia_gerada))

        self.producao = energia_gerada

    def conecta_monitoramento(self, host="127.0.0.1", port=5123):
        # Iniciamos um socket IPv4 e TCP
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Tentamos fazer a conexao com o cliente
        try:
            soc.connect((host, port))
        except:
            print("Erro durante a conexao: " + str(sys.exc_info()))
            sys.exit()

        # Iniciada a conexao -
        print("Pressione 'quit' para sair")

        # Pegamos o input da turbina
        message = input(" >> ")

        # Enquanto a mensagem for diferente de quit (para sair)
        while message != 'quit':
            # Envia a mensagem com encode de utf-8
            soc.sendall(message.encode("utf8"))

            #TODO o que acontecera se nao receber o - e sim --
            # Caso receba um '-' continue
            response = soc.recv(5120).decode("utf8")

            if response == "--":
                print('~~~~ TESTE ~~~~')
                pass        # null operation

            if response == "easter":
                print('~~~~ EASTER EGG ~~~~')
                pass        # null operation

            # Coleta nova mensagem do cliente para o monitoramento
            message = input(" >> ")

        # Envia --quit-- quando usuario escreve 'quit'
        soc.send(b'--quit--')

    def envia_mensagem(self, categoria_mensagem):
        # Iniciamos um socket IPv4 e TCP
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Tentamos fazer a conexao com o cliente
        try:
            soc.connect((self.host, self.port))
        except:
            print("Erro durante a conexao: " + str(sys.exc_info()))
            sys.exit()

        # Iniciada a conexao
        print("Turbina " + str(self.id) + ' conectada ao monitoramento')

        # Mensagem para registro da turbina no monitoramento
        if categoria_mensagem == 0:
            # A mensagem de inicio é a mais curta, mostrando apenas o ID da turbina e seu status como desligadas
            mensagem = str(categoria_mensagem) + str(self.id) + str(self.status)

            print('Enviando mensagem de '+ str(sys.getsizeof(mensagem.encode('utf8'))) +' BYTES')

            soc.sendall(mensagem.encode('utf8'))

            # Esperamos uma resposta de "OK" do monitoramento
            resposta = soc.recv(5120).decode('utf8')

            if resposta == "1":
                print('recebeu 1')
                # TODO turbina esta online e pode operar
            if resposta == "0":
                print('recebeu 0')
                # TODO algo errado com o monitoramento
            else:
                print('Deu ruim na comunicacao')

            print('Enviando QUIT '+ str(sys.getsizeof("--quit--".encode('utf8'))) +' BYTES')
            soc.send('--quit--'.encode('utf8'))

    def __str__(self):
        return self.id

if __name__ == "__main__":
    turbina = Turbina('WTG01', '127.0.0.1', 5123)
