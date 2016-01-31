drop table if exists product;
create table product (
	id integer primary key autoincrement not null,
	name text not null,
	price integer not null
);

drop table if exists purchase;
create table purchase (
	id integer primary key autoincrement not null,
	email text not null,
	handle text not null,
	nonce text not null,
	paid integer default 0,
	removed integer default 0,
	created_at text not null,
	removed_at text default '',
	paid_at text default '',
	comments text default ''
);

drop table if exists purchase_items;
create table purchase_items (
	id integer primary key autoincrement not null,
	purchase_id integer,
	product_id integer,
	n integer not null,
	foreign key(purchase_id) references purchase(id),
	foreign key(product_id) references product(id)
);

insert into product (name, price) values
	( 'ticket_business', 512 ),
	( 'ticket_premium', 256 ),
	( 'ticket_supporter', 128 ),
	( 'ticket_padawan', 64 ),
	( 'tshirt_yellow_s', 20 ),
	( 'tshirt_yellow_m', 20 ),
	( 'tshirt_yellow_l', 20 ),
	( 'tshirt_yellow_xl', 20 ),
	( 'tshirt_red_s', 20 ),
	( 'tshirt_red_m', 20 ),
	( 'tshirt_red_l', 20 ),
	( 'tshirt_red_xl', 20 ),
	( 'tshirt_green_s', 20 ),
	( 'tshirt_green_m', 20 ),
	( 'tshirt_green_l', 20 ),
	( 'tshirt_green_xl', 20 );
