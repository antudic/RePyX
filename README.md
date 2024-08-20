# RePyX
Remote Python eXecutor

This project allows you to monitor as well as modify your python code remotely
any time and from any where you want without having to restart the running code.
In your project, simply import and start the Server which will run in the 
background using Threads and then connect to the server using the Client class
from your remote machine. Using the server, you can read variables as well as
define new variables and modify existing variables in your code, all while it's
running.

## Server setup
Import this library into your code using `from repyx import Server` and then
create a server instance by doing `s = Server()`.
The default options for IP and port are 127.0.0.1 and 1337 respectively
After the instance has been created, start the threaded receiver by calling
the `s.start()` method which will continuously listen for new clients.
All commands received by the server will be interpreted as `eval()` commands
unless the string starts with "exec" in which case the following code will
be ran using the `exec()` method instead using the global scope to define
variables.

## Client setup
To connect to the server, create a Client instance by running the code
using an interactive python shell by doing `c = Client()`. Connect to the
Server by doing `c.connect()` and then either send commands by calling the
`c.sendCmd()` method or by running the console by doing `c.start()` which
continuously read from stdin and then send that to the server and print out
the return value retrieved from the server.
