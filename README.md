
# About project:
## The project has implemented a taxi system. Upon the client's request, a car corresponding to the level of the order will be dispatched. For instance, an economy-class car cannot be assigned to a business-class order, whereas a business-class car can be assigned to an economy-class order. Furthermore, when creating an order, the system considers the distance between cars and the client, which prevents drivers from accepting orders from different cities. PostGIS is used to store geolocation data in points

# How to get
    git clone https://github.com/kirillsev1/taxi.git

    python3.10 -m venv ./venv

    . ./venv/bin/activate

    pip install -r requirements.txt

# Docker container for DB:
    docker run -d --name taxi -p 5999:5432 \
    -v $HOME/postgresql/taxi/:/var/lib/postgresql/taxi \
    -e POSTGRES_PASSWORD=12345678 \
    -e POSTGRES_USER=taxi_user \
    -e POSTGRES_DB=taxi_db \
    postgis/postgis

### Create .env file near manage.py
### Fill the .env file
### Now move to project directory with manage.py
### Run start server command
    python3 manage.py runserver
    
    or
        
    ./manage.py runserver
# REST
### Token locates in database. So, select it from table:
    psql -h 127.0.0.1 -p 5435 -U your_app your_db - [Connection to database]
    enter password: - [POSTGRES_PASSWORD=...]
    SELECT * FROM token; - [User and token]

|  Authorization   | user {token}                                 |
|------------------|----------------------------------------------|
| Authorization    | admin {a1b2c3d4-a1b2-c3d4-e5f6-a1b2c3a1b2c3} |

### Postman
#### Get example
url: http://127.0.0.1/rest/driver/
#### Post example
url: http://127.0.0.1:8000/rest/Driver/

auth headers:

| Authorization    | admin {a1b2c3d4-a1b2-c3d4-e5f6-a1b2c3a1b2c3} |
|------------------|----------------------------------------------|

body:

    {
        "user": {
            "username": "tsst",
            "password": "23",
            "first_name": "test",
            "last_name": "test",
            "email": "123@gmail.com"
        },
        "phone": "31243123541",
        "car": {
            "manufacturer": "123",
            "capacity": "5",
            "number": "123",
            "mark": "123",
            "rate": "1"
        }
    }
#### Delete example
url: http://127.0.0.1:8000/rest/Car/

auth headers:

| Authorization    | admin {a1b2c3d4-a1b2-c3d4-e5f6-a1b2c3a1b2c3} |
|------------------|----------------------------------------------|

body:
    
    {
        "manufacturer": "test3",
        "capacity": 5,
        "number": "123adc",
        "mark": "new1",
        "rate": "economy"
    }


# Models

    class UUIDMixin(models.Model):
        id
_    

    class Car(UUIDMixin):
        created
        manufacturer
        capacity
        number
        mark
        rate
_
    
    class Driver(UUIDMixin):
        user
        car 
        phone
        location
_
    
    class Customer(UUIDMixin):
        user
        phone 
_
    
    class CarOrder(UUIDMixin):
        car
        order
_

    class Order(UUIDMixin):
        created
        customer
        driver
        rating
        departure
        order_date
        arrival
        cost
        rate
        status
# .env
    PG_DBNAME - database name

    PG_HOST - database host

    PG_PORT - database port

    PG_USER - database user

    PG_PASSWORD - database password