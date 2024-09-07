# OBSERVER SERVICE
- ADD TO DOCS : if a issue comes with docker volumes being downloaded and this causeing an issue , then just delete the prev dataset source and the entrypoint script will resolve stuff
- ADD TO DOCS: add timeout support to API docs relevant to stopping , session id list for start endpoint supposrt add to API docs
- file dump  reason of stoping as well - stop endpoint , full completion
- measure time in csv dump for nfig session id 

# SCORING SCRIPT
- uses our observer endpoint , gets the data
- gets the data from portkey based on the csv present in it
- computes score using absolutes ( socre 1 = sucess , everything else is failure ) dumps report as asbolute_report
- computes scores using average_scores and invalids ( things we terminiated due to timeout)
- after scores add , time analytics , step count , api call count , token coonsumption , cost , api call types , etc

analytics api from portkey - contains time duration as well ~ Maneesh chetan

# TRIMMING DEBUGGER SCRIPT
- I could write an endpoint to iterate through the entire list and then get goals that are valid and their fixed urls ( this is for debugging )
- Test out if 2x 10k batches has less goals than 1x 20k batches. Try out similar combinations after trimming to see if goals lost in between have a pattern, if no pattern then we eed to compute the relations between datasets to trim them.