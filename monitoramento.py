"""."""

import socket
import sys
from threading import Thread
import random
import time

class Monitoramento:
    """
        HOST/PORT: Host e porta que serão usados para receber as mensagens das turbinas

    """
    def __init__(self, host, port, numero_turbinas):
        self.host = host
        self.port = port

        # Definimos o numero de turbina para, no listen limitarmos o numero de conexões a porta. 5 parece um numero razoavel para os testes
        self.numero_turbinas = numero_turbinas

        # Implementacao simples de 'serial' - em uma versão mais detalhada, isso seria feito por códigos com validacao de ambos os lados
        self.seriais = ['4Y7B1N8K', 'LJAXC7SP', '3ZOPA1N7', '1MKC6KK0', '9H10W0A7']

    # Inicia servidor
    def inicia_servidor(self):
        # Cria novo socket utilizando IPv4 e TCP
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_REUSEADDR diz ao S.O para reutilizar o socket local em WAIT, sem esperar pelo time natural de expire
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Tentamos fazer bind a porta - caso esta esteja ocupada, irá falhar e o programa ira fechar
        try:
            soc.bind((self.host, self.port))
        except:
            print("Erro ao fazer 'bind' na porta: " + str(sys.exc_info()))
            sys.exit()

        # Caso o bind seja um sucesso, abrimos para uma fila de ate 5 conexoes
        soc.listen(self.numero_turbinas)

        print("--- Iniciando monitoramento ---")

        # Iniciamos um loop inifito, sempre aceitando novas conexoes
        while True:
            # Aceita a nova conexao do cliente
            connection, address = soc.accept()
            # Identificamos qual o IP e a PORTA que o cliente se encontra
            ip, port = str(address[0]), str(address[1])
            # print("Nova turbina conectada: " + ip + ":" + port)

            # Para essa nova conexao, iniciamos uma nova thread, e passamos como argumento os detalhes da conexao (socket do cliente), IP e a PORTA
            try:
                Thread(target=self.thread_turbina, args=(connection, ip, port)).start()
            except:
                print("Aconteceu algum erro ao criar a Thread")
                print(str(sys.exc_info()))

        # Por ultimo fechamos o socket do pai
        soc.close()

    # Thread que ira cuidar de toda conexao de um novo cliente
    def thread_turbina(self, connection, ip, port, max_buffer_size = 5120):
        # Bool que define se cliente ainda esta conectado | mantemos a thread ativa enquanto isso
        _ativa = True

        # Mantemos a conexao enquanto o cliente estiver ativo (recebendo pacotes ou nao saiu da aplicacao)
        while _ativa:

            # Recebemos a mensagem do cliente | aqui colocamos um buff generico de 5120B, mas poderiamos ter feito específico pro length de cada mensagem
            mensagem_turbina = connection.recv(max_buffer_size)

            # Medimos qual o length da mensagem, e de acordo com o tamanho, sabemos qual o tipo de mensagem
            length_mensagem = sys.getsizeof(mensagem_turbina)

            """ ######## INICIO CONTROLE DE MENSAGENS ######## """

            if length_mensagem == 42:
                """ FECHANDO CONEXAO COM O MONITORAMENTO """
                connection.close()
                _ativa = False

            elif length_mensagem == 38:
                """ CONFIGURANDO A TURBINA PELA PRIMEIRA VEZ """
                self.configura_turbina(connection, mensagem_turbina.decode('utf8'), ip, port)

            elif length_mensagem == 47:
                """ CONFIGURANDO A TURBINA PELA PRIMEIRA VEZ """
                resultado = self.configura_turbina_hash(connection, mensagem_turbina.decode('utf8'), ip, port)

                # caso resultado seja igual a um, o serial que a turbina nos enviou nao consta na nossa lista, então recusamos a conexao
                if resultado == 1:
                    connection.close()
                    _ativa = False

            elif length_mensagem == 51:
                """ STATUS DE TURBINA """
                self.processa_status_turbina(connection, mensagem_turbina.decode('utf8'))

            elif length_mensagem == 46:
                """ TURBINA TRIPADA / COM FALHA """
                self.process_turbina_tripada(connection, mensagem_turbina.decode('utf8'))

            else:
                """ MENSAGEM AINDA NAO CONFIGURADA """
                print('MENSAGEM NAO CONFIGURADA:')
                print(mensagem_turbina.decode('utf8'))
                print("Cliente enviou mensagem de " + str(sys.getsizeof(mensagem_turbina)) + " BYTES")

    def configura_turbina(self, connection, mensagem_turbina, ip, port):
        # Turbina esta pronta para operar
        print('Turbina ' + mensagem_turbina + ' configurada com sucesso!')

        # Envia OK para turbina de qql forma, não existe como recusar
        connection.sendall("001".encode("utf8"))

    def configura_turbina_hash(self, connection, mensagem_turbina, ip, port):
        # Igual ao metodo para configurar turbina normalmente, porém aqui fazemos o split para separar a mensagem que vem no formato WTGXX:SERIAL
        hash_turbina = mensagem_turbina.split(':')

        # Verificamos se é um serial valido
        if hash_turbina[1] in self.seriais:
            print('Turbina ' + hash_turbina[0] + ' configurada com sucesso!')
            connection.sendall("001".encode("utf8"))
        else:
            print('Erro ao analisar serial, verifique novamente')
            connection.sendall("002".encode("utf8"))
            return 1

    def processa_status_turbina(self, connection, mensagem_turbina):

        # Os parametros da turbina veem separados todos por : em formato de string
        kpis_turbina = mensagem_turbina.split(':')

        # Mandamos um print para o monitoramento
        print('Status ' + mensagem_turbina[:5] + ' => VENTO: {} | MW GERADO: {} | #ALARMES: {}'.format(kpis_turbina[1], kpis_turbina[2], kpis_turbina[3]))


        """ ###### CONDICOES PARA CONTINUAR OPERANDO ###### """

        # Caso o vento seja > 19m/s => desligamos a turbina
        if (float(kpis_turbina[1]) > 19):
            connection.sendall("002".encode("utf8"))

        # Caso o vento seja < 11m/s, aumentamos a potencia para gerar mais energia
        elif (float(kpis_turbina[1]) < 11):
            connection.sendall("003".encode("utf8"))

        # Caso o numero de falhas seja igual a 2, reduzimos a potencia a fim de causar novas falhas
        elif (float(kpis_turbina[3]) == 2):
            connection.sendall("004".encode("utf8"))

        # Caso nenhum dessas condições seja verdade, continuamos normalmente
        else:
            connection.sendall("001".encode("utf8"))

    # Quando a turbina envia uma mensagem que está tripada / com falha, apenas printamos e retornamos 'ok'
    def process_turbina_tripada(self, connection, mensagem_turbina):
        print('Turbina: ' + mensagem_turbina[:5] + ' tripada... aguardando reparos...')
        connection.sendall('001'.encode('utf8'))

if __name__ == "__main__":
    monitoramento = Monitoramento('127.0.0.1', 5123, 5)
    monitoramento.inicia_servidor()
