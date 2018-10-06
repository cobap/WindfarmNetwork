"""."""

import socket
import sys
import math
import time

class Turbina:

    def __init__(self, id, host, port):
        self.id = id
        self.status = 0
        self.host = host
        self.port = port

        self.envia_mensagem(0)

    def inicia_turbina(self):
        self.alarmes = 0
        time.sleep(100)

        self.status = 1
        self.fator_absorcao = 0.7
        # self.fator_transformacao = vento_atual/(self.alarmes + 1)

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

        if categoria_mensagem == 0:
            mensagem = str(self.id) + str(self.status)
            soc.sendall(mensagem.encode('utf8'))
            resposta = soc.recv(5120).decode('utf8')

            if resposta == "1":
                print('recebeu 1')
                # TODO turbina esta online e pode operar
            if resposta == "0":
                print('recebeu 0')
                # TODO algo errado com o monitoramento
            else:
                print('Deu ruim na comunicacao')
            soc.send(b'--quit--')
            # soc.send('--quit--'.encode('utf8'))

    def __str__(self):
        return self.id

if __name__ == "__main__":
    turbina = Turbina('WTG01', '127.0.0.1', 5123)
    print('Ligando turbina: ' + str(turbina))

    # turbina.calcula_producao(1,1,1)
