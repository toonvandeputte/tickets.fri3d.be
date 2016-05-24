-- drop user 'fr1ckets'@'localhost';
create user 'fr1ckets'@'localhost' identified by 'flotilla';
grant all on fr1ckets.* to 'fr1ckets'@'localhost';

drop database if exists fr1ckets;
create database fr1ckets;
use fr1ckets;

drop table if exists product;
create table product (
	id integer auto_increment not null,
	name varchar(64) not null,
	display varchar(64) not null,
	price float not null,
	volunteering_price float not null,
	max_dob datetime not null,
	billable integer not null,
	primary key (id)
);

insert into product (name, display, price, volunteering_price, max_dob, billable) values
	( 'ticket_3bit',     '3bit 0-3 jaar',                  8, 8, '2013-08-15 02:00:00', 0),
	( 'ticket_4bit',     '4bit 3-6 jaar',                  16, 16, '2010-08-15 02:00:00', 0),
	( 'ticket_5bit',     '5bit 6-12 jaar',                 32, 32, '2004-08-15 02:00:00', 0),
	( 'ticket_6bit',     '6bit 12-24 jaar',                64, 56, '1992-08-15 02:00:00', 0),
	( 'ticket_7bit',     '7bit +24 jaar',                  128, 112, '1900-01-01 00:00:00', 0),
	( 'ticket_8bit',     '8bit zakelijk',                  309.76, 309.76, '1900-01-01 00:00:00', 1),
	( 'tshirt_adult_m_xs',  'volwassenen mannen tshirt XS',       20, 20, '', 0),
	( 'tshirt_adult_m_s',  'volwassenen mannen tshirt S',       20, 20, '', 0),
	( 'tshirt_adult_m_m',  'volwassenen mannen tshirt M',      20, 20, '', 0),
	( 'tshirt_adult_m_l',  'volwassenen mannen tshirt L',       20, 20, '', 0),
	( 'tshirt_adult_m_xl', 'volwassenen mannen tshirt XL', 20, 20, '', 0),
	( 'tshirt_adult_m_xxl', 'volwassenen mannen tshirt XXL', 20, 20, '', 0),
	( 'tshirt_adult_f_xs',  'volwassenen vrouwen tshirt XS',       20, 20, '', 0),
	( 'tshirt_adult_f_s',  'volwassenen vrouwen tshirt S',       20, 20, '', 0),
	( 'tshirt_adult_f_m',  'volwassenen vrouwen tshirt M',      20, 20, '', 0),
	( 'tshirt_adult_f_l',  'volwassenen vrouwen tshirt L',       20, 20, '', 0),
	( 'tshirt_adult_f_xl', 'volwassenen vrouwen tshirt XL', 20, 20, '', 0),
	( 'tshirt_adult_f_xxl', 'volwassenen vrouwen tshirt XXL', 20, 20, '', 0),
	( 'tshirt_kid_xs', 'kinderen 3-4 jaar tshirt', 20, 20, '', 0),
	( 'tshirt_kid_s', 'kinderen 5-6 jaar tshirt', 20, 20, '', 0),
	( 'tshirt_kid_m', 'kinderen 7-8 jaar tshirt', 20, 20, '', 0),
	( 'tshirt_kid_l', 'kinderen 9-11 jaar tshirt', 20, 20, '', 0),
	( 'tshirt_kid_xl', 'kinderen 12-14 jaar tshirt', 20, 20, '', 0),
	( 'token',           'dranktoken',                    1.5, 1.5, '', 0);
	
drop table if exists reservation;
create table reservation (
	id integer auto_increment not null,
	email varchar(128) not null unique,
	discount integer default 0,
	available_from datetime not null,
	claimed integer default 0,
	claimed_at datetime default null,
	comments text default null,
	primary key (id),
	index reservation_email_index (email asc)
);

insert into reservation (email, discount, available_from) values
	('default',           0,  '2016-06-01 19:00:00.000000');

drop table if exists purchase;
create table purchase (
	id integer auto_increment not null,
	reservation_id integer,
	email varchar(128) not null,
	nonce varchar(128) not null,
	payment_code varchar(128) not null unique,
	queued integer default 0,
	once_queued integer default 0,
	paid integer default 0,
	removed integer default 0,
	billed integer default 0,
	created_at datetime not null,
	removed_at datetime default null,
	paid_at datetime default null,
	billed_at datetime default null,
	dequeued_at datetime default null,
	comments text default '',
	business_name text default '',
	business_address text default '',
	business_vat text default '',
	primary key (id),
	index purchase_nonce_index (nonce asc),
	constraint purchase_reservation_id_fk foreign key (reservation_id) references reservation (id) on delete set null on update cascade
);

drop table if exists purchase_history;
create table purchase_history (
	id integer auto_increment not null,
	purchase_id integer,
	created_at datetime not null,
	creator varchar(128) not null,
	event text,
	primary key (id),
	index purchase_history_purchase_id_index (purchase_id asc),
	constraint purchase_history_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update set null
);

drop table if exists purchase_items;
create table purchase_items (
	id integer auto_increment not null,
	purchase_id integer,
	product_id integer,
	n integer not null,
	person_name text not null,
	person_dob date not null,
	person_volunteers_during integer not null,
	person_volunteers_after integer not null,
	person_food_vegitarian integer not null,
	primary key (id),
	constraint purchase_items_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update cascade,
	constraint purchase_items_product_id_fk foreign key (product_id) references product (id) on delete set null on update cascade
);
