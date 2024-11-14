# **SDN com ONOS e Openflow no AWS EC2**

Esta prática foi elaborada como um exercício da disciplina [Computação em Nuvem](https://github.com/glaucogoncalves/cc) ofertada pelo PPGEE/UFPA.

A atividade trabalha a implantação de um controlador ONOS para controle de uma rede Openflow emulada via Mininet. Usaremos uma instância EC2 na AWS para instalação das ferramentas, de modo a garantir um ambiente comum. A prática ainda exercita alguns casos de uso básicos com o ONOS.

## **Pré-requisitos**

- Conta AWS ativa.
- Chave PEM (arquivo `.pem`) gerada durante a criação das instâncias EC2.
- Familiaridade com SSH e comandos de shell no linux.

---

## **1. Criando e configurando a instância EC2**

1. **Crie uma instância EC2**: dê o nome de sua preferência e garanta a seleção das opções abaixo:
   - Tipo: `t2.large` (Ubuntu 24.04).
   - **Gere ou selecione uma chave SSH** para acessar a instância.
   - **Crie um novo grupo de segurança** para a instância, este grupo será modificado depois.
   - Modifique a configuração de **armazenamento para 20 GiB**.
   - Clique em **Executar Instância**.

2. Retorne à tela de instâncias e modifique o grupo de segurança:
   - Adicione nas **Inbound Rules** a liberação para a porta `8181`, protocolo `TCP`, para qualquer origem (`0.0.0.0/0`)

3. Conectando-se via SSH

   - Se estiver usando Linux, certifique-se de que as permissões da chave .pem estão configuradas corretamente:

```bash
chmod 400 /caminho/para/sua-chave.pem
```

   - Para conectar-se a uma instância EC2 via SSH no Linux:

```bash
ssh -i /caminho/para/sua-chave.pem ubuntu@<IP-PUBLICO-DA-EC2>
```

## **2. Instalando o Docker**

Para maior facilidade de instalação dos componentes, usaremos containeres Docker tanto para o ONOS quanto para o Mininet.

1. Clone o Repositório

Primeiro, **clone este repositório** na VM criada para garantir que todos os arquivos e configurações da prática estejam acessíveis.

```bash
git clone https://github.com/glaucogoncalves/cc-sdn.git
```

2. Instale o Docker

Acesse o diretório `scripts`

```bash
cd cc-sdn/scripts
```

Execute o script de instalação do docker e siga quaisquer instruções solicitadas, se houver.

```bash
sudo ./install-docker.sh
```

## **3. Instalação e configuração do ONOS**

### **Instalação do ONOS**

Execute o comando abaixo para obter a imagem do container do ONOS

```bash
sudo docker pull onosproject/onos
```

Em seguida, **execute o ONOS**

```bash
sudo docker run -d -p 8181:8181 -p 6653:6653 onosproject/onos
```

Confira se o container está sendo executado

```bash
sudo docker ps
```

Você deveria ver uma instância do container do ONOS, similar ao exposto abaixo:

```bash
CONTAINER ID   IMAGE              COMMAND                  CREATED          STATUS          PORTS                                                                                                                NAMES
ae45172595a5   onosproject/onos   "./bin/onos-service …"   41 minutes ago   Up 41 minutes   6640/tcp, 0.0.0.0:6653->6653/tcp, :::6653->6653/tcp, 8101/tcp, 9876/tcp, 0.0.0.0:8181->8181/tcp, :::8181->8181/tcp   distracted_bhaskara
```

Observe que, se tudo ocorreu bem, o status do conteiner fica como `Up`. Observe ainda que o container ganha um `CONTAINER ID` e um nome (neste caso `distracted_bhaskara`), escolhidos pelo Docker.

### **Configuração do ONOS**

Como padrão, o ONOS possui três interfaces de gerenciamento diferentes: WebUI, CLI e RST API. Nesta prática iremos utilizar as três, iniciando pela WebUI. Para acessá-la, use umm navegador de sua escolha e acesse o endereço: `http://<IP-PUBLICO-DA-EC2>:8181/onos/ui`. Na tela de login use o usuário padrão `onos`e a senha `rocks`

**Atenção**: estamos em um ambiente de teste e estamos com esta porta acessível de todo lugar. Esta não é considerada uma boa prática para um serviço de produção.

Na sequência, após o login, clicando no menu hamburguer (canto superior esquerdo) escolha a opção *Applications*. Procure pelas aplicações abaixo, uma de cada vez. Ao encontrar uma aplicação, selecione-a e clique no botão *Activate* (triângulo na parte superior, lado direito).

	OpenFlow Agent	
	OpenFlow Base Provider
	OpenFlow Provider Suite

Estas aplicações deixam o ONOS pronto para reagir e configurar switches Openflow, os quais serão criados na próxima etapa.

## **4. Instalação do mininet e emulação da topolgia**

### **Instalação do Mininet**

Para emulação de uma rede openflow usaremos o Mininet, ferramenta que permite a criação de uma topologia de switches emulados em uma única máquina. Novamente usaremos um container docker apenas pela praticidade.

Para instalar a imagem do mininet use o comando a seguir:

```bash
sudo docker pull iwaseyusuke/mininet
```

O comando abaixo executa o container Mininet. Observe que o diretório `netemu` é mapeado para o container (`-v`), deixando os arquivos deste diretório acessíveis internamente no container.

```bash
sudo docker run -it --rm --privileged -v /lib/modules:/lib/modules -v ./netemu:/root/netemu  iwaseyusuke/mininet
```

Perceba que após a execução do comando acima, o terminal vai mudar indicando que os comandos dados agora são executados no container. Este container é efêmero (`--rm`) e caso você saia deste terminal (comando `exit`), o container será parado e removido, necessitando que o comando acima seja executado novamente.

### **Emulação da Topologia Openflow**

O próximo passo consiste na execução do programa que cria a topologia de switches Openflow. 

Usando o editor de sua preferência verifique o conteúdo do arquivo `net.py` no diretório `netemu`. A função `createTopo()` mostra a topologia que será criada a qual é formada por quatro hosts e três switches, interligados.

Após analisar o arquvio. Execute o comando abaixo:

```bash
python3 netemu/net.py
```

Ao final deste comando, você estará no menu CLI do Mininet. Este menu permite a execução de diferentes comandos e experimentos. Uma apresentação mais profunda do Mininet está fora do escopo desta prática, aqui introduziremos apenas alguns comandos úteis. Execute o comando abaixo, que faz um ping de cada host para cada outro host.

```bash
pingall
```

A saída do comando deve parecer com o mostrado abaixo. O que significa que embora os links e switches estejam ativos, não há conectividade entre os hosts, já que o ONOS ainda não configurado para reagir.

```bash
*** Ping: testing ping reachability
h1 -> X X X 
h2 -> X X X 
h3 -> X X X 
h4 -> X X X 
*** Results: 100% dropped (0/12 received)
```

## **5. Casos de Uso**

### **Comportamento básico**

Na WebUI do ONOS, clique no menu hamburguer e procure a opção *Topology*, que exibe uma visualização da topolgia da rede. A visualização mostra os hosts, swicthes e enlaces. Caso não esteja vendo os hosts, aperte o botão `h`. Para mais comandos de visualização aperte o botão `\`.

Em seguida, na opção *Applications*, ative a aplicação **Reactive Forwarding**. Esta aplicação faz com os switches façam o encaminhamento de pacotes baseados no endereço MAC dos hosts. Pacotes ARP são encaminhados normalmente (broadcast).

Retorne ao CLI do Mininet e execute o comando abaixo novamente.

```bash
pingall
```

Você deveria obter uma saída como abaixo. Indicando que há conectividade entre todos os hosts.

```bash
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
```

**Atenção**: Caso ainda haja um ou mais entradas com o valor `X` na saída do comando `pingall`, ative a aplicação Proxy ARP/NDP, que garante que os pacotes ARP serão tratados diretamente pelo controlador, evitando quaisquer problemas de conectividade via broadcast.

Ainda no CLI do Mininet, execute um `ping` do host `h1` para `h3` usando o comando a seguir:

```bash
h1 ping h3
```

Deixe executando e acesse a opção *Devices* na WebUI do ONOS. Selecione o switch `of:0000000000000002` e clique em *Show flow view for selected device* (terceiro ícone no alto do lado direito). Esta tela vai mostrar **os fluxos Openflow instalados pelo controlador** para tratar o ping. Analise e procure entender a lógica dos fluxos a partir do que vimos em sala. Você pode interromper o ping (digitando *Ctrl+C* no CLI do Mininet) e verificar quais fluxos são removidos.

### **Firewall**

Na WebUI do ONOS, ative a aplicação *Access Control Lists* que habilita um sistem de firewall simples no ONOS. O comportamento do firewall é permitir todo o tráfego entre os hosts, exceto entre os pares de hosts bloqueados na lista de controle de acesso. A lista que será instalada no ONOS está descrita no arquivo `firewall.csv`.

A configuração do firewall ocorre por meio de uma API REST. Para ver as regras de controle de acesso instaladas acesse, por meio de uma aba do navegador, a URL: `http://<IP-PUBLICO-DA-EC2>:8181/onos/v1/acl/rules`. Esta API retorna um JSON contendo as regras instaladas. Neste momento não há regras e a mensagem de retorno deve ser similar à saída abaixo.

```json
{"aclRules":[]}
```

Lendo o arquivo `firewall.csv`, é possível ver que bloquearemos o tráfego de h1 para h3 e de h2 para h4. Para instalar as regras de controle de acesso, acesse sua instância EC2 com um novo terminal SSH (ou seja, não use o mesmo terminal onde o Mininet está sendo executado).

Em seguida, usando o editor de sua preferência, modifique o script `fw.py`, adicionando o IP de sua instância EC2 e execute-o:

```bash
python3 fw.py
```

Verifique, por meio da API REST, que as regras foram instaladas. Para confirmar o comportamento na rede, execute o comando `pingall` no CLI do Mininet. A saída do comando deve ser parecida com a que vai abaixo.

```bash
*** Ping: testing ping reachability
h1 -> h2 X h4 
h2 -> h1 h3 X 
h3 -> X h2 h4 
h4 -> h1 X h3 
*** Results: 33% dropped (8/12 received)
```

Para remover as regras de bloqueio, modique o arquivo `rm-fw.py` adicionando o IP de sua instância EC2 e execute-o.

```bash
python3 rm-fw.py
```

 Verifique a remoção das regras pela API REST no navegador e teste com o comando `pingall`. Sua saída deve ser como abaixo:

```bash
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
```

### **Intents**

Outra forma de realizar o encaminhamento de pacotes por meio do ONOS é através dos *Intents*, que se trata de uma funcionalidade do ONOS que permite especificar o comportamento da rede na forma de políticas, ao invés de mecanismos. Em outras palavras: diz-se a rede o que se deseja e não como fazer. O exemplo a seguir explora esta funcionalidade. Além disso, veremos o uso da API REST do ONOS.

Antes de continuar, desative a aplicação *React Forwarding*. Isso vai fazer com que os hosts na rede tornem-se novamente inalcançáveis entre si.

Para usar a API REST acesse, usando seu navegador, a documentação na URL: `http://<IP-PUBLICO-DA-EC2>:8181/onos/v1/docs/`. Esta é uma documentação completa da API suportada pelo ONOS, e que pode ser diretamente executada nesta página.

Procure pela opção *Intents* e clique em *Show/Hide*. Você verá todas os recursos da API com uma breve descrição intuitiva. Clique na opção `POST /intents` (em verde). No campo *stream* cole o JSON abaixo e clique em *Try it out!*:

```json
{
  "type": "HostToHostIntent",
  "appId": "org.onosproject.ovsdb",
  "priority": 55,
  "one": "00:00:00:00:00:01/-1",
  "two": "00:00:00:00:00:03/-1"
}
```

Esta configuração informa que você deseja que os hosts `h1` e `h3` estejam conectados. Contudo note que você não informa como isso deve acontecer. Tal decisão fica a cargo do ONOS.

Em seguida teste o comando `pingall` no CLI do Mininet. Você deveria ver conectividade apenas entre `h1` e `h3`.

**Atenção**: Caso não haja conectividade entre `h1` e `h3`, ative a aplicação Proxy ARP/NDP.

Você pode observar que o *Intent* foi criado usando o WebUI do ONOS. Clique no menu hamburguer e selecione a opção *Intents*. Você pode ainda ver o intent na topologia, selecionando-o e clicando na opção *Show selected intent on topology view* (terceiro ícone no canto superior direito). Você verá o intent como uma linha tracejada laranja na interface do ONOS.

Verifique agora o que acontece quando o enlace que está sendo usado falha. No CLI do Mininet digite o comando abaixo e observe a WebUI do ONOS, você deve notar uma mudança na rota escolhida pelo ONOS.

```bash
link s2 s3 down
```

Antes de prosseguir, restabeleça o enlace:

```bash
link s2 s3 up
```

Agora iremos remover o intent.

De volta a API REST do ONOS em seu navegador. Procure o recurso `GET /intents` (em azul) e clique no botão *Try it out!*. Observe o retorno e procure pela entrada `"key": "0x05"`. O número desta entrada `key` será diferente do mostrado neste exemplo. Anote-o para uso a seguir.

Procure o recurso `DELETE /intents` (em vermelho). No campo `appId` digite `org.onosproject.ovsdb` e no campo `key` digite o valor encontrado no passo anterior. Finalmente, clique no botão *Try it out!*.

Repita o comando `pingall` no CLI do Mininet. Você vai observar que não há mais comunicação entre os hosts.

### **Virtual Private LAN Service (VPLS)**

Neste caso de uso, vamos implementar uma VPLS que é uma rede multiponto de hosts geograficamente separados que compartilham um enlace de broadcast, ou seja, **os sistemas finais que pertencem à VPLS se comunicam como se estivessem em uma LAN**. Como exemplo, criaremos uma VPLS entre os hosts `h1`, `h2` e `h4`. Desta forma o host `h3` restará inacessível a esta rede.

Neste caso de uso, usaremos também a interface CLI do ONOS. Para este caso de uso você deve acessar sua instância EC2 com um terminal SSH diferente do terminal onde o Mininet está sendo executado.

Inicie removendo a aplicação *Proxy ARP/NDP* pela WebUI do ONOS e ative a aplicação *VLAN L2 Broadcast Network*. 

Em seguida, acesse o terminal de sua instância EC2 e execute o comando abaixo, substituindo o `<CONTAINER-ID>` pelo identificador do container do ONOS (para obter o identificador do container execute `sudo docker ps`):

```bash
sudo docker exec -it <CONTAINER-ID> bash
```

O comando acima irá executar um terminal no container. Para ter acesso ao CLI do ONOS primeiramente precisaremos instalar um cliente SSH no container. Para isso use os comandos a seguir:

```bash
apt update
apt install openssh-client
```

Por fim, execute o comando abaixo para acesso ao CLI do ONOS. Quando a senha for solicitada digite `karaf`.

```bash
cd bin
./onos -l karaf
```

Caso a conexão ao CLI ocorra com sucesso você deve visualizar uma mensagem como abaixo:

```bash
Welcome to Open Network Operating System (ONOS)!
     ____  _  ______  ____     
    / __ \/ |/ / __ \/ __/   
   / /_/ /    / /_/ /\ \     
   \____/_/|_/\____/___/     
                               
Documentation: wiki.onosproject.org      
Tutorials:     tutorials.onosproject.org 
Mailing lists: lists.onosproject.org     

Come help out! Find out how at: contribute.onosproject.org 

Hit '<tab>' for a list of available commands
and '[cmd] --help' for help on a specific command.
Hit '<ctrl-d>' or type 'logout' to exit ONOS session.

karaf@root >   
```

No CLI do ONOS inicie verfiicando os hosts descobertos pelo ONOS, digitando o comando `hosts`. Note que este comando exibe uma saída similar a que encontramos na opção *Hosts* da WebUI.

Na saída do comando hosts (ou na WebUI) observe a informação `locations`, que indica o switch Openflow e a interface deste switch a qual o host está ligado. Por exemplo, a saída abaixo mostra que o host `00:00:00:00:00:01` está conectado ao switch `of:0000000000000002` pela interface `3` deste switch.

```bash
id=00:00:00:00:00:01/None, mac=00:00:00:00:00:01, locations=[of:0000000000000002/3], auxLocations=null, vlan=None, ip(s)=[10.0.0.1], innerVlan=None, outerTPID=unknown, provider=of:org.onosproject.provider.host, configured=false
```

A informação de `locations` é importante para o próximo passo que envolve a criação de rótulos no ONOS para cada interface a qual cada host se conecta. Em nossa topologia, os hosts `h1`, `h2` e `h4` conectam-se à rede, respectivamente, através das interfaces `of:0000000000000002/3`, `of:0000000000000002/4` e `of:0000000000000003/4`. Os comandos abaixo rotulam as interfaces citadas com os nomes `h1`, `h2` e `h4` e as deixam prontas para uso na VPLS.

```bash
interface-add of:0000000000000002/3 h1
interface-add of:0000000000000002/4 h2
interface-add of:0000000000000003/4 h4
```

Agora crie a `vpls1` e adicione as interfaces usando o comando abaixo. Use o comando `vpls show vpls1` após a execução para visualizar a VPLS criada.

```bash
vpls create vpls1
vpls add-if vpls1 h1
vpls add-if vpls1 h2
vpls add-if vpls1 h4
```

Use o comando `pingall` no CLI do Mininet para testar a conectividade. A saída deve ser similar a que está abaixo:

```bash
*** Ping: testing ping reachability
h1 -> h2 X h4 
h2 -> h1 X h4 
h3 -> X X X 
h4 -> h1 h2 X 
*** Results: 50% dropped (6/12 received)
```

Uma VPLS do ONOS é criada utilizando o conceito de *Intents* que vimos anteriormente. Pela WebUI, acesse a aopção *Intents* do menu hamburguer e verifique os intents criados. Aqui três SinglePointToMultiPointIntents foram criados. Estes servem para comunicar o tráfego broadcast (ARP) entre os hosts. Além disso, podemos ver que três MultiPointToSinglePointIntents foram criados, os quais são usados para o tráfego unicast.

Para finalizar, adicione a interface do host `h3` à VPLS e reexecute o comando `pingall`. Agora todos os hosts devem estar se comunicando.
