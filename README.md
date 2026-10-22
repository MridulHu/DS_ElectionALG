# Lab Exercise 4 — Bully Leader Election

## Requirements
- Run all nodes on the same machine using localhost TCP ports 5001–5005
- If more nodes need to be created then you can create duplicate files and change id. doing so ill also change the port address since it is 5000 + n.

## Run
Open five terminals and run all files namely node1.py, node2.py, node3.py, node4.py, node5.py

## Test Scenarios ##
** Normal Scenario: ** After running all the files manually each of them elect themselves as the leader  by sending " I am Leader " and after the other coordinator dont reply the node ith the highest identifier is elected as the leader


** Leader Crash: ** Terminate the program running ith the highest identifier anad check hether the loer processes ping and notice that leaader ith the higher identifier has crashed and start reelection and elect themselves until a process ith  higher identifier elects itself.


** Recovery: ** STart the program ith the highest value that you crashed earlier and run it again and it sends message that i am leader and since it has the highest identifier it get elected as the leader.


** Folloer Crash: ** This time instead of terminating the process ith highest value e select a process ith loer value than the leader and see that the leader remains unchanged.

** Cascading failure: ** No e terminate all the processes in descending order and see that henver e terminate a leader then next process hich is loer to it get elected and this cycle keeps happening until all the processes terminate.



