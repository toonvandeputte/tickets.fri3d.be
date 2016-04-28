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
	( 'ticket_6bit',     '6bit 12-24 jaar',                72, 64, '1992-08-15 02:00:00', 0),
	( 'ticket_7bit',     '7bit +24 jaar',                  144, 128, '1900-08-15 02:00:00', 0),
	( 'ticket_8bit',     '8bit zakelijk',                  256, 256, '1900-08-15 02:00:00', 1),
	( 'tshirt_adult_s',  'volwassenen tshirt small',       20, 20, '', 0),
	( 'tshirt_adult_m',  'volwassenen tshirt middle',      20, 20, '', 0),
	( 'tshirt_adult_l',  'volwassenen tshirt large',       20, 20, '', 0),
	( 'tshirt_adult_xl', 'volwassenen tshirt extra large', 20, 20, '', 0),
	( 'tshirt_kid_s',    'kinder-tshirt small',            20, 20, '', 0),
	( 'tshirt_kid_m',    'kinder-tshirt middle',           20, 20, '', 0),
	( 'tshirt_kid_l',    'kinder-tshirt large',            20, 20, '', 0),
	( 'tshirt_kid_xl',   'kinder-tshirt extra large',      20, 20, '', 0),
	( 'token',           'dranktoken',                    1.5, 1.5, '', 0);
	
drop table if exists reservation;
create table reservation (
	id integer auto_increment not null,
	email varchar(128) not null,
	discount integer default 0,
	available_from datetime not null,
	claimed integer default 0,
	claimed_at datetime default null,
	comments text default null,
	primary key (id),
	index reservation_email_index (email asc)
);

insert into reservation (email, discount, available_from) values
	('default',           0,  '2016-06-01 19:00:00.000000'),
	('jef.vdb@gmail.com', 10, '2015-06-01 19:00:00.000000');

drop table if exists purchase;
create table purchase (
	id integer auto_increment not null,
	reservation_id integer,
	email varchar(128) not null,
	nonce varchar(128) not null,
	payment_code varchar(128) not null unique,
	queued integer default 0,
	paid integer default 0,
	removed integer default 0,
	created_at datetime not null,
	removed_at datetime default null,
	paid_at datetime default null,
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
