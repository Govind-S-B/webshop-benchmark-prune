# OBSERVER SERVICE
- ADD TO DOCS : tip test out /abc before kicking off a new session after a fresh deployment up
- ADD TO DOCS : if a issue comes with docker volumes being downloaded and this causeing an issue , then just delete the prev dataset source and the entrypoint script will resolve stuff ( indexing issues and all )
- ADD TO DOCS: add timeout support to API docs relevant to stopping , session id list for start endpoint supposrt add to API docs
- ADD TO DOCS : support for termination cause in status anc cleanup endpoints
- ADD TO DOCS : metrics captured in csv file

- add support for stop reason as error in API or some other exception ( each session or full observation )

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

None in csv not written - handle commas explicitly
termination status stopped even after good complete completion , no completed satus is ever written 