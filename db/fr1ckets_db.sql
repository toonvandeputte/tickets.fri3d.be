drop table if exists product;
create table product (
	id integer primary key autoincrement not null,
	name text not null,
	display text not null,
	price float not null,
	volunteering_price float not null,
	max_dob timestamp not null,
	billable integer not null
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
	( 'token',           'dranktoken',                    1.5, 20, '', 0);
	
drop table if exists reservation;
create table reservation (
	id integer primary key autoincrement not null,
	email text not null,
	discount integer default 0,
	available_from timestamp not null,
	claimed integer default 0,
	claimed_at text default '',
	comments text default ''
);
create unique index if not exists index_reservation_email on reservation(email);

insert into reservation (email, discount, available_from) values
	('default',           0,  '2016-06-01 19:00:00.000000'),
	('jef.vdb@gmail.com', 10, '2015-06-01 19:00:00.000000');

drop table if exists purchase;
create table purchase (
	id integer primary key autoincrement not null,
	reservation_id integer,
	email text not null,
	nonce text not null,
	queued integer default 0,
	paid integer default 0,
	removed integer default 0,
	created_at text not null,
	removed_at text default '',
	paid_at text default '',
	comments text default '',
	business_name text default '',
	business_address text default '',
	business_vat text default '',
	foreign key(reservation_id) references reservation(id)
);
create unique index if not exists index_purchase_nonce on purchase(nonce);

drop table if exists purchase_history;
create table purchase_history (
	id integer primary key autoincrement not null,
	purchase_id integer,
	created_at text not null,
	event text,
	foreign key(purchase_id) references purchase(id)
);

drop table if exists purchase_items;
create table purchase_items (
	id integer primary key autoincrement not null,
	purchase_id integer,
	product_id integer,
	n integer not null,
	person_name text not null,
	person_dob integer not null,
	person_volunteers_during integer not null,
	person_volunteers_after integer not null,
	person_food_vegitarian integer not null,
	foreign key(purchase_id) references purchase(id),
	foreign key(product_id) references product(id)
);
