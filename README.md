# WindfarmNetwork

(Proposta *detalhada* da aplicação) - WindfarmNetwork é um simulador da rede de um parque eólico. Uma windfarm (como normalmente são conhecidos) é composto por multiplas turbinas (clientes) e uma central de monitoramento (servidor). Durante o dia a dia dessas turbinas, é necessário uma comunicação segura e rápida com o monitoramento, afim de repassar 'status' de cada um dos sensores presentes nos mais de 1000 componentes da turbina, e notificar a central sobre eventuais falhas. Com isso, automaticamente a central consegue auxiliar o controlador da turbina sobre como reagir a cenário pré-definidos. Mas há também os casos, quando a turbina excede o numero de alarmes (um threshold) que é conhecido como 'tripagem', onde a turbina precisa de uma manutenção in-loco.

O objetivo desse pequeno projeto é simular como seria um protocolo de comunicação simples entre essas turbinas e seu respectivo monitor. Não foram adicionados 'sensores' nessas turbinas, porém, para compensar, foram descritas algumas funções (vento, geração de energia, fator de transformação do vento, etc) que visam tornar o projeto um "toy-model" da realidade. Além disso, como não é possível simular manutenções reais nesses equipamentos, para cada falha ou delay de comunicação, foi posto de ~timer~ que visa simular situações adversas de turbinas fora de comunicação ou que demoram a responder

## Especificação da comunicação

Para desenvolver o projeto, utilizamos da arquitetura de cliente-servidor, no qual as turbinas estão representando diversos clientes, que a todo momento estão trocando informações com o servidor (que é a central de monitoramento). A ideia é que tenhamos um servidor multithread, afim de em paralelo lidar com multiplas requisições e decisões sobre a performance das turbinas. Para o caso de testes, forma utilizados no máximo 3 turbinas simultaneamente, mas nada impede de expandir essa arquitetura para lidar com simulações maiores (+100 turbinas)

O programa foi separado em 2 arquivos: 'turbina.py' e 'monitoramento.py'. Este primeiro, guarda todas as informações da turbina, como e.g geração do vento, fator de transformação do vento (o quanto está transformando o vento em energia mecanica) e até mesmo o numero de falhas que a turbina possui atualmente. Enquanto isso, no monitoramento, temos guardado toda a lógica de como essas turbinas devem se comportar conforme determinados padrões de mensagens: Se uma turbina estiver com o vento acima de 19m/s, ela deve ser desligada e retornar após 10s de espera. Isso faz com que simulemos açoes básicas que um monitoramento real faz com turbinas no dia a dia.

Mas específicamente, foi-se posto uma abordagem em que, tirando as tomadas de decisões, toda a lógica seria pertencente a turbina: controle de falhas, mudanças de potencia de maquina, etc. Todos os casos sitados são pequenas variáveis que a propria turbina ou o monitoramento podem ter controle e manipular conforme desejarem. Além disso, a turbina é responsável por a cada 5 segundos, enviar uma nova mensagem ao monitoramento com os resultados do ultimo 'loop' de geração.

Um importante ponto a mencionar aqui. Existem 2 tipos possíveis de comunicação entre turbinas e monitoramento, depende da arquitetura dos desenvolvedores da turbina. Este pode ser feito em batches ou em real-time. Assim, primeiramente em real-time, teriamos um socket aberto que a todo instante mandaria dados sobre todos os sensores da turbina. Como deve-se imaginar, apesar de ser o melhor tipo de comunicação para coleta de dados e decisões, acaba trazendo muitos problemas ao dia-a-dia do monitoramento, devido (1) inconsistencia na rede entre turbina e monitoramento; (2) falhas que afetam os controladores; (3) projetos mal desenhados que acabam conflitando pacotes e informações. Por tentarmos simular o mais proximo projetos de comunicação entre turbinas que se assemalham da realidade, obtamos então pela 2 opção, que consiste em abrir um socket de comunicação com o monitoramento toda vez que um batch de dados estiver pronto para ser enviado.

Nesse caso, em nosso projeto, as Turbinas estão a cada 5segundos coletando os dados de vento e geração de energia - podendo nesse meio tempo gerar falhas e até mesmo tripar. Com os 5 segundos finalizados, as turbinas então enviam uma grande mensagem para o monitoramento monstrando a média das informações geradas no ultimo 'loop'. No caso da nossa simulação, geramos os dados somente 1vez e esperamos 5segundos para gera-los novamente, aproximando nossa simulação do modelo real mais confiante.

## Protocolo de comunicação

 -> TCP vs UDP
 -> sintaxe e semântica
 -> parâmetros da mensagem
 -> como escrevo a mensagem
 -> como respondo essas mensagens
 -> explicações gerais do pq fizemos assim

## Como instalar e executar a simulação

Mandar links, etc. Fonte de dados e uso o programa

## Como ler o código

(main está em tal classe, etc) Diagrama

## Quais testes vcs fizeram e quais resultados nos obtivemos

## Problemas de rede e implementação

Pq aconteceu e como resolver


PENDENTE:
Proposta *detalhada* da aplicação

Especificação da comunicação (pode colocar ideias)
 -> cliente servidor
 -> como
 -> o que tá no cliente/servidor
 -> o que cada um faz
 -> como lidar com erro
 -> segurança / criptografia
 -> temporizacao (iteração em tempo real)

Protocolo de comunicação bem especificado (ver Livro)
 -> TCP vs UDP
 -> sintaxe e semântica
 -> parâmetros da mensagem
 -> como escrevo a mensagem
 -> como respondo essas mensagens
 -> explicações gerais do pq fizemos assim


## Fonte
usar fontes e comentar no código da onde veio

entregar fonte relatório e executável
