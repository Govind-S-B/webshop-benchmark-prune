ADD TO DOCS : if a issue comes with docker volumes being downloaded and this causeing an issue , then just delete the prev dataset source and the entrypoint script will resolve stuff

new nedpoint : status - gets if thing finished running or not , if running which was the last run session , we could reuse the same variable for run status for this

add logic to skip to next session after 12 minutes , this is the timeout limit.

log session id , and time and the log file name in my side , call it at the termination of each thread , dump data on a csv


ADDITIONAL SCRIPT : I could write an endpoint to iterate through the entire list and then get goals that are valid and their fixed urls ( this is for debugging )
analytics api from portkey - contains time duration
next step in pipeline  write script to get both data and tabulate them , make 2 scores

status endpoint

shift to logic to load userids to process than using ranges , or a fallabcke to ranges if not resovled