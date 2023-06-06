USE z5r;

INSERT IGNORE INTO DIR_Card (CardId)
(select 101) union
(select 102) union
(select 103) union
(select 110) union
(select 120);

INSERT IGNORE INTO DIR_User (Name)
(select 'Некто') union
(select 'Немо') union
(select 'Человек') union
(select 'Человек без карты');

INSERT IGNORE INTO OPT_User_Cards (ID_User, ID_Card)
(select 1,1) union
(select 1,6) union
(select 2,2) union
(select 3,3);