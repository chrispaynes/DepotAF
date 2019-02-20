SET TIME ZONE 'UTC';

CREATE SCHEMA alpha;

-- CREATE ADMIN ROLE
CREATE ROLE admin WITH LOGIN SUPERUSER CREATEDB CREATEROLE REPLICATION NOINHERIT PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE depotaf to admin;
ALTER ROLE admin SET search_path = alpha;

-- ALTER READ_WRITE USER ROLE
GRANT ALL PRIVILEGES ON DATABASE depotaf to postgres;
GRANT CONNECT ON DATABASE depotaf TO postgres;
GRANT USAGE ON SCHEMA alpha TO postgres;
GRANT CREATE ON SCHEMA alpha TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA alpha TO postgres;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA alpha TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA alpha TO postgres;
ALTER ROLE postgres SET search_path TO alpha, public;
ALTER ROLE postgres WITH NOINHERIT;

create table if not exists alpha.category (
	category_id serial not null,
	category_name	varchar(100) not null,
	constraint category_name_k unique(category_name),
	constraint category_id_pk primary key (category_id)
);

create table if not exists alpha.notecard (
	notecard_id serial not null,
	question varchar not null,
	answer varchar not null,
	correct_submissions	smallint default 0,
	incorrect_submissions	smallint default 0,
	constraint question_k unique (question),
	constraint notecard_id_pk primary key (notecard_id)
);

create table if not exists alpha.notecard_categories (
	notecard_id integer references alpha.notecard(notecard_id),
	category_id integer references alpha.category(category_id),
	constraint notecard_category_pk primary key (notecard_id, category_id)
);

insert into alpha.category(category_name) values
	('Algebra'),
	('Calculus'),
	('Convolutional Neural Networks (CNNs)'),
	('Data Visualization'),
	('Deep Learning'),
	('Generative Adversarial Networks (GANs)'),
	('Neural Networks'),
	('Trigonometry'),
	('Statistics'),
	('SQL');