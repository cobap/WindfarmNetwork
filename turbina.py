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
        # Definimos o nome da turbina na linha de comando, considerando sempre o primeiro argumento
        self.id = sys.argv[1]

        # Caso tenhamos um segundo argumento, utilizamos como serial da turbina
        if len(sys.argv) == 3:
            self.serial = sys.argv[2]

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

        # Temos o fator de transformacao, que baseado na quantidade de alarmes, do vento atual e da potencia que a maquina esta, transforma x % do vento em energia
        self.fator_transformacao = self.vento_atual * ((self.potencia)**(1-self.alarmes))

        # Repetimos isso indefinidamente
        while True:

            # 1 - Verificamos se a turbina ja esta configurada e rodando normalmente
            if self.status == 1:

                # Geramos o vento desse 'loop'
                self.vento_atual = (random.random() * 10) + 10

                # recalculamos o fator de transformacao
                fator_transformacao = self.vento_atual * ((self.potencia)**(1-self.alarmes))

                # e recalculamos a energia gerada
                self.energia_gerada = (math.cos(tempo) + 2) * 1/fator_transformacao

                # Dependendo da velocidade do vento, temos uma determinada chance de um alarme aparecer
                chance_alarme = 0
                if self.vento_atual > 16:
                    chance_alarme = 0.3
                elif self.vento_atual > 13:
                    chance_alarme = 0.2
                elif self.vento_atual > 11:
                    chance_alarme = 0.1
                else:
                    chance_alarme = 0.05

                # Vemos se ocorre um alarme na turbina
                if random.random() < chance_alarme:
                    self.alarmes = self.alarmes + 1

                # Printamos a geração
                print('VENTO: {} | ALARMES: {} | FATOR TRANSF: {} | CHANCE_ALARME: {} | ENERGIA GERADA: {}'.format(self.vento_atual, self.alarmes, fator_transformacao, chance_alarme, self.energia_gerada))
                print('--------------')

                # Caso a turbina tenha alcançado 3 alarmes, ela tripou e precisa aguardar 30segundos para retornar
                if self.alarmes == 3:
                    print('TRIPOU')

                    # Dorme 15segundos
                    time.sleep(15)

                    # Resetamos o status com 0 alarmes e como operacional
                    self.alarmes = 0
                    self.status = 1

                    # Enviamos uma mensagem ao monitoramento que a turbina está tripada
                    self.envia_mensagem(2)

                # Caso nao tenha 3 alarmes, enviamos uma mensagem de categoria 1 = simples status de operacao
                self.envia_mensagem(1)

                # Dormimos 5 segundos
                time.sleep(5)

            # Caso a turbina esteja desligada, paramos por 15 segundos e depois retomamos
            elif self.status == 2:
                print('TURBINA PARADA')
                time.sleep(15)

            # Caso o monitoramento demore para responder e a turbina esteja tripada, ela irá dormir +30 segundos
            elif self.status == 3:
                print('TURBINA TRIPADA')
                time.sleep(30)

    # Metodo que controla todas as mensagens que a turbina pode enviar
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

            # Mensagem = somente o ID da turbina
            mensagem = str(self.id)

            # Caso a turbina tenha sido configurada com um serial, automaticamente mudamos a mensagem para contar o serial
            if hasattr(self, 'serial'):
                mensagem = str(self.id) + ':' + str(self.serial)

            # Chamamos o metodo que lida com essa mensagem
            self.configura_turbina(soc, mensagem)

        elif categoria_mensagem == 1:
            """ -- STATUS DA TURBINA -- """

            # Mensagem com vento, energia gerada e #alarmes
            mensagem = str(self.id) + ':{:.2f}:{:.2f}:{}'.format(self.vento_atual, self.energia_gerada, self.alarmes)

            # Chamamos o metodo que lida com essa mensagem
            self.processa_status_turbina(soc, mensagem)

        elif categoria_mensagem == 2:
            """ -- TURBINA TRIPOU -- """

            # Abaixamos a potencia da turbina
            self.potencia = 0.3

            # Mensagem do ID da turbina e seu status de tripped
            mensagem = str(self.id) + ':TRIPPED'

            # Chamamos o metodo que lida com essa mensagem
            self.process_turbina_tripada(soc, mensagem)

    def configura_turbina(self, connection, mensagem):

        # Enviamos a mensagem para o monitoramento
        connection.sendall(mensagem.encode('utf8'))

        # Esperamos uma resposta de "OK" do monitoramento
        resposta = connection.recv(5120).decode('utf8')

        # Caso resposta seja 'OK'
        if resposta == "001":
            print('Monitoramento configurou turbina com sucesso!')
            # Configuramos turbina para rodar
            self.status = 1
        else:
            # Ocorreu um erro de rede / serial - fechamos o programa
            print('Ocorreu um erro durante configuracao da turbina')
            sys.exit(1)

        # Mandamos request para fechar a conexao
        mensagem = 'EXIT' + self.id
        connection.send(mensagem.encode('utf8'))


    def processa_status_turbina(self, connection, mensagem):

        # Enviamos a mensagem para o monitoramento
        connection.sendall(mensagem.encode('utf8'))

        # Esperamos as orientacoes do monitoramento
        resposta = connection.recv(5120).decode('utf8')

        # Turbina está ok e deve permanecer rodando
        if resposta == '001':
            print('TURBINA RODANDO')
        # Devemos desligar a turbina por 10 segundos
        elif resposta == '002':
            print('DESLIGA TURBINA')
            time.sleep(10)

            # Configuramos a potencia para 0.3 devido a alta do vento
            self.potencia = 0.3

        elif resposta == '003':
            print('AUMENTA POTENCIA')

            # Aumentamos a potencia 1 nivel | caso esteja no maximo nao faz nada
            if(self.potencia == 0.3):
                self.potencia = 0.5
            elif(self.potencia == 0.5):
                self.potencia = 0.7

        elif resposta == '004':

            # Diminui a potencia 1 nivel | caso esteja no minimo nao faz nada
            print('DIMINUI POTENCIA')
            if(self.potencia == 0.7):
                self.potencia = 0.5
            elif(self.potencia == 0.5):
                self.potencia = 0.3

        else:
            print('STATUS NAO DEFINIDO')
            # Caso a mensagem nao esteja configurada corretamente

        # Fechamos a conexao
        mensagem = 'EXIT' + self.id
        connection.send(mensagem.encode('utf8'))

    def process_turbina_tripada(self, connection, mensagem):
        connection.sendall(mensagem.encode('utf8'))

        # Esperamos as orientacoes do monitoramento
        resposta = connection.recv(5120).decode('utf8')

        # Caso o monitoramento retorne 'ok', ele reconheceu que a turbina esta tripada e esta aguardando reparos...
        if resposta == '001':
            print('MONITORAMENTO AGUARDANDO REPARO')

        # Fechamos a conexao
        mensagem = 'EXIT' + self.id
        connection.send(mensagem.encode('utf8'))

        # Mandamos a turbina dormir 15segundos para reiniciar
        time.sleep(15)

    def __str__(self):
        return self.id

if __name__ == "__main__":
    turbina = Turbina('127.0.0.1', 5123)
    turbina.iniciar()
