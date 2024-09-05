I am working on this observer script that monitors a log and saves sessions and does a bunch of stuff. it works along with the webshop service as seen in @docker-compose.yaml file. 

I want this to function like this ideally

There are 2 sub components actually one is the actual thing observing the logs and montioring the logs for events and generates url kinda thing and sends API requests to a foreing API server (marked as comments for now) you can read the @observer_script.py to know more about how and what it does

I want also an API componenent , this is to actually control and restart the observer in cases
so there are 3 things - clean , start , stop  , save(with a name) , get(with a name)

clean will clean all the contents in the user_session_logs/mturk directory , this is so that when running new sessions they can start from an empty state

stop will stop the observer with the last session_id it processed , basically abandon any session_id it was currenlty processing

start will create a new session and can accept params like what range is it work with ( this basically indicates the test case size ) , when the observer iterates through all this it will automatically stop observer

save accepts a name and moves the logs within mturk folder to a new folder within that name

get accepts a name will compress the older with the name and sends it back as a zip file or something like that

How should i actually architecture this observer and the observers api , is it unwise to have these 2 things done by a single service. I think since logically this is the function of a single observer ( to be able to observe and be controlled ) they should be a single service. But should i break this down into observer-observer and observer-api or something like this but then this will introduce complexities in handling communication as well no ?