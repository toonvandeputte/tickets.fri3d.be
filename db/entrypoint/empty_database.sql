CREATE SCHEMA IF NOT EXISTS `fr1ckets` DEFAULT CHARACTER SET utf8mb4;
USE `fr1ckets`;

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
	( 'ticket_3bit',     '3bit 0-3 jaar',                  7, 7, '2015-08-18 02:00:00', 0),
	( 'ticket_4bit',     '4bit 3-6 jaar',                  17, 17, '2012-08-18 02:00:00', 0),
	( 'ticket_5bit',     '5bit 6-12 jaar',                 37, 37, '2006-08-18 02:00:00', 0),
	( 'ticket_6bit',     '6bit 12-24 jaar',                73, 73, '1994-08-18 02:00:00', 0),
	( 'ticket_7bit',     '7bit +24 jaar',                  157, 137, '1900-01-01 00:00:00', 0),
	( 'ticket_8bit',     '8bit zakelijk',                  317, 317, '1900-01-01 00:00:00', 1),
	( 'tshirt_adult_m_xs',  'volwassenen mannen tshirt XS',       20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_m_s',  'volwassenen mannen tshirt S',       20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_m_m',  'volwassenen mannen tshirt M',      20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_m_l',  'volwassenen mannen tshirt L',       20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_m_xl', 'volwassenen mannen tshirt XL', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_m_xxl', 'volwassenen mannen tshirt XXL', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_f_xs',  'volwassenen vrouwen tshirt XS',       20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_f_s',  'volwassenen vrouwen tshirt S',       20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_f_m',  'volwassenen vrouwen tshirt M',      20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_f_l',  'volwassenen vrouwen tshirt L',       20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_f_xl', 'volwassenen vrouwen tshirt XL', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_adult_f_xxl', 'volwassenen vrouwen tshirt XXL', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_kid_xs', 'kinderen 3-4 jaar tshirt', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_kid_s', 'kinderen 5-6 jaar tshirt', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_kid_m', 'kinderen 7-8 jaar tshirt', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_kid_l', 'kinderen 9-11 jaar tshirt', 20, 20, '1900-01-01 00:00:00', 0),
	( 'tshirt_kid_xl', 'kinderen 12-14 jaar tshirt', 20, 20, '1900-01-01 00:00:00', 0),
	( 'token',           'dranktoken',                    1.5, 1.5, '1900-01-01 00:00:00', 0),
	( 'ticket_vip_all', 'VIP ticket voor alle dagen', 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket_vip_friday', 'VIP ticket voor vrijdag', 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket_vip_saturday', 'VIP ticket voor zaterdag', 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket_vip_sunday', 'VIP ticket voor zondag', 0, 0, '1900-01-01 00:00:00', 0),
	( 'ticket_vip_monday', 'VIP ticket voor maandag', 0, 0, '1900-01-01 00:00:00', 0),
	( 'badge_robot_parts', 'Robot parts', 17, 17, '1900-01-01 00:00:00', 0);

drop table if exists reservation;
create table reservation (
	id integer auto_increment not null,
	email varchar(128) not null unique,
	available_from datetime not null,
	claimed integer default 0,
	claimed_at datetime default null,
	comments text,
	primary key (id),
	index reservation_email_index (email asc)
);
insert into reservation (email, available_from) values
	('default', '2018-05-13 22:00:00'),
	('someone@who.reserved', '2018-04-30 22:00:00');

drop table if exists purchase;
create table purchase (
	id integer auto_increment not null,
	email varchar(128) not null,
	nonce varchar(128) not null,
	payment_code varchar(128) not null unique,
	reservation_id integer,
	transportation varchar(64) not null,
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
	comments text,
	business_name text,
	business_address text,
	business_vat text,
	primary key (id),
	index purchase_nonce_index (nonce asc),
	constraint purchase_reservation_id_fk foreign key (reservation_id) references reservation (id) on delete restrict on update cascade
);

drop table if exists voucher;
create table voucher (
	id integer auto_increment not null,
	code varchar(128) not null unique,
	discount integer default 0,
	claimed integer default 0,
	claimed_at datetime default null,
	reason text,
	comments text,
	purchase_id integer,
	primary key (id),
	index voucher_code_index (code asc),
	constraint voucher_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete set null on update cascade
);


drop table if exists purchase_voucher;
create table purchase_voucher (
	id integer auto_increment not null,
	purchase_id integer,
	voucher_id integer,
	primary key (id),
	constraint purchase_voucher_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update cascade,
	constraint purchase_voucher_voucher_id_fk foreign key (voucher_id) references voucher (id) on delete cascade on update cascade
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
	person_name text null,
	person_dob date null,
	person_volunteers_before integer not null,
	person_volunteers_during integer not null,
	person_volunteers_after integer not null,
	person_food_vegitarian integer not null,
	primary key (id),
	constraint purchase_items_purchase_id_fk foreign key (purchase_id) references purchase (id) on delete cascade on update cascade,
	constraint purchase_items_product_id_fk foreign key (product_id) references product (id) on delete set null on update cascade
);

drop table if exists shift_time;
create table shift_time (
	id integer auto_increment not null,
	description varchar(64) not null,
	day integer not null,
	primary key (id)
);
drop table if exists shift_post;
create table shift_post (
	id integer auto_increment not null,
	what varchar(64) not null,
	description text,
	primary key (id)
);
drop table if exists `shift`;
create table `shift` (
	id integer auto_increment not null,
	shift_time_id integer,
	shift_post_id integer,
	persons integer,
	comments text,
	primary key (id),
	constraint shift_shift_time_id_fk foreign key (shift_time_id) references shift_time (id) on delete set null on update cascade,
	constraint shift_shift_post_id_fk foreign key (shift_post_id) references shift_post (id) on delete set null on update cascade
);

drop table if exists shift_volunteer;
create table shift_volunteer (
	id integer auto_increment not null,
	purchase_item_id integer,
	shift_id integer,
	primary key (id),
	constraint shift_volunteer_shift_id_fk foreign key (shift_id) references shift (id) on delete set null on update cascade,
	constraint shift_volunteer_purchase_item_id_fk foreign key (purchase_item_id) references purchase_items (id) on delete set null on update cascade
);

insert into shift_time (description, day) values
	( 'Vrijdag 18:00 - 21:00', 1 ),
	( 'Vrijdag 21:00 - einde', 1 ),
	( 'Zaterdag 09:00 - 12:00', 2 ),
	( 'Zaterdag 12:00 - 15:00', 2 ),
	( 'Zaterdag 15:00 - 18:00', 2 ),
	( 'Zaterdag 18:00 - 21:00', 2 ),
	( 'Zaterdag 21:00 - einde', 2 ),
	( 'Zondag 09:00 - 12:00', 3 ),
	( 'Zondag 12:00 - 15:00', 3 ),
	( 'Zondag 15:00 - 18:00', 3 ),
	( 'Zondag 18:00 - 21:00', 3 ),
	( 'Zondag 21:00 - einde', 3 ),
	( 'Maandag 09:00 - 12:00', 4 ),
	( 'Maandag 12:00 - 15:00', 4 ),
	( 'Maandag 15:00 - 18:00', 4 ),
	( 'Maandag 18:00 - 21:00', 4 );

insert into shift_post (what, description) values
	( 'Bar', 'De toog bemannen en drank verschaffen, de koelkast en het koffiemachien bijvullen, een snackje serveren.' ),
	( 'Infodesk', 'Toekomers ontvangen, vragen beantwoorden, tokens verkopen, special guests en content bringers van informatie voorzien, oogje op de meteo houden.'),
	( 'Vliegende keeper', 'Enkel de meest willekeurige taken zijn goed genoeg voor de vliegende keeper! Mensen zoeken, gasten doorverwijzen, last minute patches...'),
	( 'Koken', 'Op zaterdag fri3tjes bakken, op zondag de BBQ bemannen. Tafels en stoelen opstellen en later weer terug zetten voor de talks & workshops.'),
	( 'Content support', 'Content-brengers helpen met opzet/afbraak van hun talks en workshops, bezoekers begeleiden, opvolgen dat het tijdsschema gerespecteerd blijft.'),
	( 'Parking/bakfietsen', 'Zodat de toekomende en vertrekkende gasten vlot hun bagage kunnen transporteren, de bakfietsen heen en weer tussen parking en kamp voeren.');

insert into `shift` (shift_time_id, shift_post_id, persons) values
	( 1, 1, 2 ),
	( 1, 2, 2 ),
	( 1, 6, 1 ),

	( 2, 1, 2 ),
	( 2, 2, 2 ),
	( 2, 6, 1 ),

	( 3, 1, 2 ),
	( 3, 2, 2 ),
	( 3, 3, 1 ),
	( 3, 6, 1 ),

	( 4, 1, 2 ),
	( 4, 2, 2 ),
	( 4, 3, 1 ),
	( 4, 5, 3 ),

	( 5, 1, 2 ),
	( 5, 2, 2 ),
	( 5, 3, 1 ),
	( 5, 4, 4 ),
	( 5, 5, 3 ),

	( 6, 1, 2 ),
	( 6, 2, 1 ),
	( 6, 3, 1 ),
	( 6, 4, 8 ),

	( 7, 1, 2 ),
	( 7, 2, 1 ),
	( 7, 3, 1 ),

	( 8, 1, 2 ),
	( 8, 2, 2 ),
	( 8, 3, 1 ),
	( 8, 5, 3 ),

	( 9, 1, 2 ),
	( 9, 2, 2 ),
	( 9, 3, 1 ),
	( 9, 5, 3 ),

	( 10, 1, 2 ),
	( 10, 2, 2 ),
	( 10, 3, 1 ),
	( 10, 4, 4 ),
	( 10, 5, 3 ),

	( 11, 1, 2 ),
	( 11, 2, 1 ),
	( 11, 3, 1 ),
	( 11, 4, 8 ),

	( 12, 1, 2 ),
	( 12, 2, 1 ),
	( 12, 3, 1 ),

	( 13, 1, 2 ),
	( 13, 2, 2 ),
	( 13, 3, 1 ),
	( 13, 5, 3 ),

	( 14, 1, 2 ),
	( 14, 2, 2 ),
	( 14, 3, 1 ),
	( 14, 5, 3 ),
	( 14, 6, 1 ),

	( 15, 1, 2 ),
	( 15, 2, 2 ),
	( 15, 3, 1 ),
	( 15, 6, 1 ),

	( 16, 1, 2 ),
	( 16, 2, 1 ),
	( 16, 3, 1 ),
	( 16, 6, 1 );


