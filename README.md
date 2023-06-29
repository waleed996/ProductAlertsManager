
# Product Alerts Manager Microservice

Following is an overview of the design and implementation and how various tools are utilized.

# Tools Used
Following are the tools and technologies utilized for this service:

1. Python
2. Django
3. Django Rest Framework
4. MySQL
5. Celery
6. Celery Beat
7. Redis
8. Pytest
9. Docker

# Design Phase 1

Following are the parts in phase 1 and an overview about the design and implementation.

## User alerts settings APIs
To implement this part, I have chosen the widely used django and django restframework. I have leveraged the 
restframework ViewSet to implement the APIs. When a user setting is created, a message is sent to a redis queue. 
The insights service in phase 2 will listen for this message and process it. For payload validation I have written
a RequestDataValidationHelper class which validates the data passed to it in a dictionary against the validation schema
defined on the API Controller/ViewSet. The user data is saved in a MySQL relational database and all interactions are
through the Django ORM.

## Sending User Emails
In an ecommerce website there are almost always a large number of users/data that the system needs to handle and
process. Scalability and performance are key in such domains. The email solution I have implemented is developed
keeping these things in mind.

I have used a distributed task queue 'Celery' to cater for the scalability and performance requirements to handle a
large number of users in a real world case. Along with celery I have used 'Celery Beat' which functions as a task
scheduler and enqueue's a master/distributor task in a redis queue every 2 minutes. This distributor task is responsible
for creating batches/parts of the data/users that need to be processed. It divides the number of users in roughly equal
parts and enqueue's subtasks in the celery queue which can be picked up by any free celery worker process or thread.
Celery uses 'Redis' as the message broker to consume messages and to coordinate with other worker processes. It's 
distributed nature allows us to scale the system by adding more nodes in the celery cluster.

For emails I have used a simple django smtp email backend as a temporary solution to complete the end to end flow.

# Design Phase 2

The solution I chose for this part of the problem is that of a shared database. Although this is only partly implemented
because of time constraints.

The celery worker picks up a subtask and starts to process it, an api call is made to the ebay product searching api to
get product data for each individual phrase configured by the user. After fetching the data from ebay, another subtask
is enqueued with celery. The job of this subtask is to prepare the ebay data into ORM objects and do a bulk insert
query in the shared database. I chose to create a separate task for this because I did not want to overload the 
email sender subtask with object creation and doing a large query to insert in the shared database. This approach 
avoids creation and network overhead on the email sender subtask providing performance benefits.

Using the shared db approach, the shared data is in a centralised place where other services
can also access and utilize it.

# Project Structure
Below is a breif description of the main components of the microservice and the rationale behind it.

### app
The app package is the main area where most of the logic of the service resides. Inside app there are some 
layers(packages) which ensures good separation in the code. The 'controller' package will contain all the views which
catch the api requests. There will be multiple modules in this package with an appropriate name. The related 
Controllers/Views will reside in the closest related module. The same rationale applies to models, 
repositories (db interaction layer), serializers and services package. The rule here is that the request will always be 
received by the controller layer which can contain any authentication or authorization logic and will then call the
appropriate method on the service layer. The service layer will contain all the business logic. Only the service layer
is supposed to interact with the repository layer unless there is an exceptional case. The Repository contains all 
the ORM queries which can be reused in different services. I find this approach to promote re-usability, beneficial 
in writing clean code and in testing.

### shared_data_app
The 'shared_data_app' is a django 'app' which is dedicated to contain any models or logic related to the shared 
databases in the microservices cluster. Each microservice can have this app to keep the shared data models and logic 
separate from rest of the code.

# API Documentation
I have used swagger for api documentation. The documentation can be used to call apis as well. When all containers are
up and running you can access the swagger docs at the following url

```http://0.0.0.0:8000/docs/swagger```

# Tests
For testing I have used Pytest. The tests are not complete because of time constraints. But the groundwork and the 
interfaces like object factories and fixtures are implemented. I added a nice mechanism for coverage report 
using `coverage` and `pytest-cov` packages, unfortunately they are not exposed, so it cannot be viewed. If you want you
can install all the dependencies in requirements.txt and run the following command

```coverage run manage.py test -v 2 && coverage report && coverage html```

This will generate a folder called 'htmlcov' inside it you can open the index.html in the browser to see a report for 
the tests. I will include a screenshot in the email when I send the task.

You can also run the tests locally, for convenience i have pushed the 'test_settings.py' to the repo. Inside this file
you will need to set the `REDIS_QUEUE_URL` variable because the POST endpoint uses it to send messages. So you should 
have redis installed locally OR you can choose to ignore this and one test will fail and the rest will pass.

To run the tests locally you need to install the requirements first using

```pip install -r requirements.txt```

After that just run the following command from the project directory.

```pytest```


# Caveats

Following are features that are missing because I barely had the time to work on this and my priority was to get an
end-to-end solution working, so you may find places where I have cut corners.

1. Only GET and POST apis are implemented for user product alert configuration settings.

2. Unit tests are not complete, but everything is nicely setup. The db, the object factories, the coverage report 
generation etc.

3. The code is not written for different environments at the moment. Ideally having more time I would have separate 
settings files base, dev, stage, prod and local with the settings variables separated env wise.

4. Phase 2 is not complete, it is only partly done. The data is saved in the shared db but the insight emails are not
implemented.

5. In the implementation of the celery tasks, these are at the moment functions inside tasks module. I wanted to 
encapsulate them in a Class based implementation but unfortunately celery was not detecting the tasks if I put them 
inside a class. I do not have the time to do more research to make that work so I have just put them in functions to 
complete the end to end flow.

6. Emails just contain the list of products. They are not formatted.

## Run Locally

Clone the project

```bash
  git clone git@github.com:waleed996/ProductAlertsManager.git
```

Make sure to have docker and docker-compose installed, Go to the project directory containing 'docker-compose.yml' , 
then run the following command.

```bash
  docker-compose up --build
```


