drop table if exists drivers, cars, customers, orders;

create extension if not exists "uuid-ossp";

create table if not exists drivers(
	id uuid primary key default uuid_generate_v4(),
	user_id int references auth_user(id),
	phone text
);

create table if not exists customers(
	id uuid primary key default uuid_generate_v4(),
	user_id int references auth_user(id)
	phone text
);

create table if not exists cars(
	id uuid primary key default uuid_generate_v4(),
	created timestamp,
	manufacturer text,
	car_class text,
	capacity int,
	number text,
	mark text
);

create table if not exists orders(
	id uuid primary key default uuid_generate_v4(),
	created timestamp,
	passenger_id uuid references passengers (id),
	car_id uuid references cars (id),
	driver_id uuid references drivers (id),
	rate decimal,
	departure text,
	order_date timestamp,
	arrival text,
	cost decimal
);
