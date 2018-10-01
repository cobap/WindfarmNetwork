"""."""

import socket
import sys

def inicia_conexao_turbina(host="127.0.0.1", port=5123):
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

if __name__ == "__main__":
    inicia_conexao_turbina()
