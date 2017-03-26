# zick_chatbot
It's a basic chatbot for messenger powered by Chatfuel
The webhook has been placed on the server at heroku and the backend is python
to make it work we need to make sure that the server is runningand also it is recommended to 
run the files in virtual environment as follows:

go to the directory containing the directory of this help

~~~
source `which virtualenvwrapper.sh`
mkvirtualenv test-bot
pip install -r requirements.txt
~~~

then to make heroku app

~~~
heroku create
git pudh heroku master
heroku open
~~~
copy the https:// link as this will act as webhook

then create a facebook page and go top developer page of facebook and create a new messenger
app and link it with the previous page and use the above link as webhook and set the verification token
then make changes in heroku too(add the tokens)
~~~
heroku config:add PAGE_ACCESS_TOKEN=<page_acs_token>
heroku config:add VERIFY_TOKEN=<verify_token>
~~~
Now all is set, link the page with the chatfuel design and it should work outside the box
