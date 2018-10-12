"""."""

import socket
import sys
import math
import time
import random

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

        POTENCIA: modo com que a turbina está produzindo: forte (0.7) | medio (0.5) | fraco (0.3)
    """

    # Ja iniciamos uma nova turbina com o IP e PORTA do monitoramento + o ID dessa turbina
    def __init__(self, host, port):
        # Definimos o nome da turbina na linha de comando
        self.id = sys.argv[1]

        # A turbina inicia desligada e com configuracao de potencia media
        self.status = 0
        self.potencia = 0.5

        # Definimos o host e porta da turbina
        self.host = host
        self.port = port

        # Enviamos uma mensagem tipo 0, para que o monitoramento registre essa turbina em sua lista e a ligue
        self.envia_mensagem(0)

    def iniciar(self):

        # Iniciamos no tempo 1 com 0 alarmes presentes
        tempo = 1
        self.alarmes = 0
        # Nosso vento sempre será aleatorio e variando de turbina a turbina
        self.vento_atual = (random.random() * 10) + 10

        # Temos o fator de transformacao, que baseado na quantidade de alarmes, do vento atual e da potencia que a maquina esta, transforma x% do vento em energia
        self.fator_transformacao = self.vento_atual * ((self.potencia)**(1-self.alarmes))

        # Repetimos isso indefinidamente
        while True:
            # 1 - Verificamos se a turbina ja esta configurada
            if self.status == 1:
                self.vento_atual = (random.random() * 10) + 10

                # Verificar pq fator não está sendo alterado pelo numero de alarmes
                fator_transformacao = self.vento_atual * ((self.potencia)**(1-self.alarmes))

                self.energia_gerada = (math.cos(tempo) + 1) * fator_transformacao

                chance_alarme = 0
                if self.vento_atual > 16:
                    chance_alarme = 0.3
                elif self.vento_atual > 13:
                    chance_alarme = 0.2
                elif self.vento_atual > 11:
                    chance_alarme = 0.1
                else:
                    chance_alarme = 0.05

                if random.random() < chance_alarme:
                    self.alarmes = self.alarmes + 1

                print('VENTO: {} | ALARMES: {} | FATOR TRANSF: {} | CHANCE_ALARME: {} | ENERGIA GERADA: {}'.format(self.vento_atual, self.alarmes, fator_transformacao, chance_alarme, self.energia_gerada))
                print('--------------')

                if self.alarmes == 3:
                    self.status = 3
                    # TODO precisa parar a turbina

                self.envia_mensagem(1)
                time.sleep(5)

            elif self.status == 2:
                print('TURBINA PARADA')
                time.sleep(10)

            elif self.status == 3:
                print('TURBINA TRIPADA')
                time.sleep(10)

    def envia_mensagem(self, categoria_mensagem, parametros=None):
        # Iniciamos um socket IPv4 e TCP
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Tentamos fazer a conexao com o cliente
        try:
            soc.connect((self.host, self.port))
        except:
            print("Erro durante a conexao: " + str(sys.exc_info()))
            sys.exit()

        # Iniciada a conexao
        # print("Turbina " + str(self.id) + ' conectada ao monitoramento')
        # print('Enviando mensagem de '+ str(sys.getsizeof(mensagem.encode('utf8'))) +' BYTES')

        if categoria_mensagem == 0:
            """ -- REGISTRO DA TURBINA -- """
            # Enviamos o label da turbina, para que o monitor reconheca uma nova configuracao
            mensagem = str(self.id)
            soc.sendall(mensagem.encode('utf8'))

            # Esperamos uma resposta de "OK" do monitoramento
            resposta = soc.recv(5120).decode('utf8')

            if resposta == "001":
                print('Monitoramento configurou turbina com sucesso!')
                self.status = 1
            else:
                print('Ocorreu um erro durante configuracao da turbina')

            # Fechamos a conexao
            mensagem = 'EXIT' + self.id
            soc.send(mensagem.encode('utf8'))

        elif categoria_mensagem == 1:
            """ -- STATUS DA TURBINA -- """
            mensagem = str(self.id) + ':{:.2f}:{:.2f}:{:.2f}'.format(self.vento_atual, self.energia_gerada, self.alarmes)
            soc.sendall(mensagem.encode('utf8'))

            # Esperamos as orientacoes do monitoramento
            resposta = soc.recv(5120).decode('utf8')

            if resposta == '001':
                # CONTINUAR
                print('CONTINUANDO TURBINA')
            elif resposta == '002':
                # PARAR devido ao vento muito alto
                print('PARANDO TURBINA')
                self.status = 2
            elif resposta == '003':
                # AJUSTAR A POTENCIA devido ao vento bom e potencia baixa
                print('AJUSTANDO POTENCIA')
            else:
                print('STATUS NAO DEFINIDO')

            # Cancela conexao
            mensagem = 'EXIT' + self.id
            soc.send(mensagem.encode('utf8'))

    def __str__(self):
        return self.id

if __name__ == "__main__":
    turbina = Turbina('127.0.0.1', 5123)
    turbina.iniciar()
