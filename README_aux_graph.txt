Modification history:

stage 1: adapt the library to an RWTA algorithm
for QKD secured optical network

1. created parameters loading scripts
  （run_quick_sim）

2. added auxgraph_demo_net network topo

3. added weight to the adjacency matrix
    to achieve this:
    changed the adjacency matrix data type
    from bool to np.float32;
    added a third parameter in get_edges
    for the auxgraph network;
    changed logics in matrix filling-in
    so that the weight can be stored;
    changed some plotting strategies;

4. added a debug function for the dijkstra
   convenient for inspecting if dijkstra is 
   working alright.
   As well helpful for auxgraph construction

5. no time-sliding window is used in this paper
   it means if a time slot is occupied, then
   find another time slot using first fit
   There are 4 wavelenghts for Qchs according 
   to the paper.
   According to this strategy and possion arrival-
   settings in the article (leave rate = 0.004/deta-t)
   holding time = 10 delta-t (temporarily not considering update),
   modified the possion arrival formula.
   Adaption for network initialzation, currently initalised 
   initial holding time to rand int 0-10.(To avoid uneven distribution)

6. originally, source and destination nodes are network attributes,
   and are static. Here, the network attribute s and d is abandoned,
   and changed to dynamic attribute attached to each request, so as 
   to stay in line with the paper(and the reality). 