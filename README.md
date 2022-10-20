ASST - Automation Support Server Template
============

:star2: [Features](#star2-features) | :robot: [How to - Server](#robot-how-to---server) | :mechanical_arm: [How to - Client](#mechanical\_arm-how-to---client) | :gear: [Run and testing](#gear-run-and-testing) | :spiral_notepad: [To do](#spiral\_notepad-to-do) | :scroll: [License](#scroll-license)

> *Asst is an abbreviation for assistant.*

This application template allows you to quickly and easily build your own automation server. It can be used in any scope: from microservices to the main server which can rule all your automation processes. It was written as a hub to automate work with backend servers but not limited to that and can be adapted for various cases. Clients for this server can be written on many program languages thanks to Socket IO which powered this project. Few client examples included as well.

ASST project was born as a proof-of-concept that two test automation frameworks written in different languages can use the same shared code base to work with backend servers. Automation servers like this one can give the possibility to develop and maintain a single code base for numerous frameworks and support tools.

<!-- Features -->
:star2: Features
---------------

- Small but powerful automation server for various scenarios
- Usage scope from microservices to main automation node
- Helps easily automate regular service tasks for backend servers and DevOps activities
- Can be used as proxy for test frameworks and as backend server for various DevOps tools
- Built to automate regular backend servers task but can be adapt for any other scenarios
- Build-in logger system allow server to send to clients statuses of tasks in real-time
- Clients able to keep constant connections with server to receive automation tasks statuses and results right away
- Clients can be written on many programming languages, such as: JavaScript, Java, C++, Swift, Dart, Python, .Net, Rust, Kotlin

<!-- How to - Server -->
:robot: How to - Server
---------------

You can find the server's code in the `/server/asst/` directory.

Server handles constant connection with clients, keeps client information such as ssh connection params, connects with these params to backend servers (*currently optimized for Linux servers*), does some work and returns results to client. Based on this approach you need to write your backend logic only once, for the server. Then all clients written in different programming languages can use the server as an automation proxy to do work on backend servers.

`main.py` - file with main server logic. It handles client connections and contains all logic to work with backend servers. Additionally there is a block of code which imports "jobs" from modules inside `jobs` folder and can generate all jobs lists for clients. Additional information can be found as comments inside the file.

`logger.py` - logger singleton module which handles python logs and is used for sending messages through SocketIO to clients.

`connector.py` - module which handles all ssh logic to work with backend servers.

`config.ini` - default server params.

<!-- How to - Client -->
:mechanical_arm: How to - Client
---------------

### Python client

Example of Python client can be found in the `/clients/client-py/asst_client` directory.

I really like the idea of making the client as easy and accessible as possible to use. To achieve this idea I made a special client module which can pull server's available commands and make a dynamic class on client side with logic to handle all server-client connections. It allows to hide server communication from client and work with this class as with a simple local module. I call it `transparent client`. You are free to use this approach as an example and build your own client on top depending on your needs.

`main.py` - main client file which contains some examples of requests to server, catch all answers from server and show a detailed log of what's going on. Additional information can be found as comments inside the file.

`client.py` - 'transparent client' module which dynamically generates python class based on commands list received from server.

`logger.py` - simple logger for client.

`config.ini` - default client params.

### TypeScript client

Example of Python client can be found in the `/clients/client-ts/` directory.

`main.ts` - very simple TS client example with few requests inside.

<!-- Run and testing -->
:gear: Run and testing
---------------

Server and examples of clients work from the box and can be started as is for test purposes. All needed environment and dependencies files you can find in directories near applications.

### Server

Start a server with `python3 server/asst/main.py` or use Dockerfile. It will start on `5000` port by default. It can be changed in `config.ini` - `port = 5000` and inside a Dockerfile - `EXPOSE 5000`. If you are going to use docker-compose configuration be sure you changed port there too.

### Client example - Python

- Change server's IP address and port, if you need to, inside `config.ini` - `[connect]` `ip = localhost` `port = 5000`
- Fill two `[serverX]` tabs with own ssh parameters (*from box will work with Linux servers*)
- Start client with `python3 clients/client-py/asst_client/main.py`

### Client example - TypeScript

- Change server's IP address if you need to inside `main.ts` - `const socket = io("http://0.0.0.0:5000");`
- Fill `emitMsg` which contains `ssh_connection_init` job with own ssh parameters (*from box will work with Linux servers*)
- Start client with `ts-node clients/client-ts/main.ts`

<!-- To do -->
:spiral_notepad: To do
---------------

- [ ] Fully move server's jobs logic to proper modules
- [ ] Standardization for server-client communication
- [ ] Rework template to full-flesh framework
- [ ] New awesome features

<!-- License -->
:scroll: License
---------------

Distributed under the [Mozilla Public License Version 2.0](http://mozilla.org/MPL/2.0/) license. See LICENSE for more information.
