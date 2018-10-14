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

                self.energia_gerada = (math.cos(tempo) + 2) * 1/fator_transformacao

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
                    print('TRIPOU')
                    time.sleep(15)
                    self.alarmes = 0
                    self.status = 1
                    self.envia_mensagem(2)

                self.envia_mensagem(1)
                time.sleep(5)

            elif self.status == 2:
                print('TURBINA PARADA')
                time.sleep(15)

            elif self.status == 3:
                print('TURBINA TRIPADA')
                time.sleep(30)

    def envia_mensagem(self, categoria_mensagem, parametros=None):
        # Iniciamos um socket IPv4 e TCP
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Tentamos fazer a conexao com o cliente
        try:
            soc.connect((self.host, self.port))
        except:
            print("Erro durante a conexao: " + str(sys.exc_info()))
            sys.exit()

        if categoria_mensagem == 0:
            """ -- REGISTRO DA TURBINA -- """

            # Mensagem somente o ID da turbina
            mensagem = str(self.id)
            self.configura_turbina(soc, mensagem)

        elif categoria_mensagem == 1:
            """ -- STATUS DA TURBINA -- """

            # Mensagem com vento, energia gerada e #alarmes
            mensagem = str(self.id) + ':{:.2f}:{:.2f}:{}'.format(self.vento_atual, self.energia_gerada, self.alarmes)
            self.processa_status_turbina(soc, mensagem)

        elif categoria_mensagem == 2:
            """ -- TURBINA TRIPOU -- """

            self.potencia = 0.3

            # Mensagem com vento, energia gerada e #alarmes
            mensagem = str(self.id) + ':TRIPPED'
            self.process_turbina_tripada(soc, mensagem)

    def configura_turbina(self, connection, mensagem):
        connection.sendall(mensagem.encode('utf8'))

        # Esperamos uma resposta de "OK" do monitoramento
        resposta = connection.recv(5120).decode('utf8')

        if resposta == "001":
            print('Monitoramento configurou turbina com sucesso!')
            self.status = 1
        else:
            print('Ocorreu um erro durante configuracao da turbina')

        # Fechamos a conexao
        mensagem = 'EXIT' + self.id
        connection.send(mensagem.encode('utf8'))

    def processa_status_turbina(self, connection, mensagem):
        connection.sendall(mensagem.encode('utf8'))

        # Esperamos as orientacoes do monitoramento
        resposta = connection.recv(5120).decode('utf8')

        if resposta == '001':
            print('TURBINA RODANDO')
            # CONTINUAR
        elif resposta == '002':
            print('DESLIGA TURBINA')
            time.sleep(10)
            self.potencia = 0.3
            # DESLIGAR TURBINA
        elif resposta == '003':
            print('AUMENTA POTENCIA')
            if(self.potencia == 0.3):
                self.potencia = 0.5
            elif(self.potencia == 0.5):
                self.potencia = 0.7
            # AUMENTAR POTENCIA
        elif resposta == '004':
            print('DIMINUI POTENCIA')
            if(self.potencia == 0.7):
                self.potencia = 0.5
            elif(self.potencia == 0.5):
                self.potencia = 0.3
            # DIMINUI POTENCIA
        else:
            print('STATUS NAO DEFINIDO')

        # Fechamos a conexao
        mensagem = 'EXIT' + self.id
        connection.send(mensagem.encode('utf8'))

    def process_turbina_tripada(self, connection, mensagem):
        connection.sendall(mensagem.encode('utf8'))

        # Esperamos as orientacoes do monitoramento
        resposta = connection.recv(5120).decode('utf8')

        if resposta == '001':
            print('MONITORAMENTO AGUARDANDO REPARO')

        # Fechamos a conexao
        mensagem = 'EXIT' + self.id
        connection.send(mensagem.encode('utf8'))

        time.sleep(15)

    def __str__(self):
        return self.id

if __name__ == "__main__":
    turbina = Turbina('127.0.0.1', 5123)
    turbina.iniciar()
