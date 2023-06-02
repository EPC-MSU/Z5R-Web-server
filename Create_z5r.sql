CREATE DATABASE IF NOT EXISTS Z5R;

USE Z5R;

DROP TABLE IF EXISTS CLS_EventType;

CREATE TABLE CLS_EventType (
   ID int auto_increment primary key,
   Name varchar(255) not null
);

DROP TABLE IF EXISTS DIR_User;

CREATE TABLE DIR_User(
    ID int auto_increment primary key,
    Name varchar(255) not null UNIQUE
);

DROP TABLE IF EXISTS DIR_Card;

CREATE TABLE DIR_Card(
    ID int auto_increment primary key,
    UniqNumber int not null UNIQUE

);

DROP TABLE IF EXISTS OPT_User_Cards;

CREATE TABLE OPT_User_Cards(
    ID int auto_increment primary key,
    ID_User int not null,
    ID_Card int not  null,
    foreign key(ID_User)
    references DIR_User(ID),
    foreign key (ID_Card)
    references DIR_Card(ID),
    unique key ID_User_Card (ID_User, ID_Card)
);

DROP TABLE IF EXISTS REG_Event;

CREATE TABLE REG_Event (
    ID int primary key,
    DT datetime not null,
    ID_EventType int, not null
    ID_Card int, null
    foreign key(ID_EventType)
    references CLS_EventType(ID),
    foreign key (ID_Card)
    references DIR_Card(ID)
);

INSERT INTO CLS_EventType  ([ID], [Name])
    select 0, 'Opened from inside on entrance',
    select 1, 'Opened from inside on exit' union
    select 2, 'Key not in database on entrance' union
    select 3, 'Key not in database on exit' union
    select 4, 'Key in database, door opened on entrance' union
    select 5, 'Key in database, door opened on exit' union
    select 6, 'Key in database, access denied on entrance' union
    select 7, 'Key in database, access denied on exit' union
    select 8, 'Door opened from network on entrance' union
    select 9, 'Door opened from network on exit' union
    select 10, 'Key in database, door locked on entrance' union
    select 11, 'Key in database, door locked on exit' union
    select 12, 'Door violation on entrance' union
    select 13, 'Door violation on exit' union
    select 14, 'Door kept open timeout on entrance' union
    select 15, 'Door kept open timeout on exit' union
    select 16, 'Passed on entrance' union
    select 17, 'Passed on exit' union
    select 20, 'Controller reboot' union
    select 21, 'Power (see flag)' union
    select 32, 'Door opened on entrance' union
    select 33, 'Door opened on exit' union
    select 34, 'Door closed on entrance' union
    select 35, 'Door closed on exit' union
    select 37, 'Mode changed (see flags)' union
    select 38, 'Controller on fire (see flags)' union
    select 39, 'Security event (see flags)' union
    select 40, 'No passage during grace period on entrance' union
    select 41, 'No passage during grace period on exit' union
    select 48, 'Gateway is entered on entrance' union
    select 49, 'Gateway is entered on exit' union
    select 50, 'Gateway blocked on entrance' union
    select 51, 'Gateway blocked on exit' union
    select 52, 'Gateway enterance allowed on entrance' union
    select 53, 'Gateway enterance allowed on exit' union
    select 54, 'Passage blocked on entrance' union
    select 55, 'Passage blocked on exit'; 