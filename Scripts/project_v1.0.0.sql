drop table if exists drivers, cars, passengers, orders;

create extension if not exists "uuid-ossp";

create table if not exists drivers(
	id uuid primary key not null default uuid_generate_v4(),
	created date not null,
	name text not null,
	age int not null,
	phone text
);

create table if not exists cars(
	id uuid primary key not null default uuid_generate_v4(),
	created date not null,
	manufacturer text not null,
	class text,
	capacity int not NULL,
	number text,
	mark text
);

create table if not exists passengers(
	id uuid primary key not null default uuid_generate_v4(),
	created date,
	name text not null,
	age int not null,
	email text not null,
	phone text
);

create table if not exists orders(
	id uuid primary key not null default uuid_generate_v4(),
	created date not null,
	passenger_id uuid references passengers (id),
	car_id uuid references cars (id),
	driver_id uuid references drivers (id),
	departure text not null,
	order_date date not null,
	arrival text not null,
	coast decimal
);