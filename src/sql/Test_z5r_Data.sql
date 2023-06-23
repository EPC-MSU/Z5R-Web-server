USE z5r;

INSERT IGNORE INTO DIR_Card (CardId)
(select 101) union
(select 102) union
(select 103) union
(select 104) union
(select 105);

INSERT IGNORE INTO DIR_User (Name)
(select 'Некто') union
(select 'Немо') union
(select 'Человек') union
(select 'Человек без карты');

INSERT IGNORE INTO OPT_User_Cards (ID_User, ID_Card)
(select 1,1) union
(select 1,4) union
(select 2,2) union
(select 3,3);


INSERT IGNORE INTO REG_Event (AnyCardId, DT, ID_EventType, Controller, Flag)
(select 320, '2023-06-13 02:02:02', 2, 'sn333', 32) union
(select 321, '2023-06-13 03:03:03', 3, 'sn333', 32) union
(select 322, '2023-06-14 04:04:04', 2, 'sn333', 32) union
(select 101, '2023-06-13 10:05:05', 5, 'sn333', 32) union
(select 103, '2023-06-13 10:07:07', 5, 'sn333', 32) union
(select 101, '2023-06-13 11:05:05', 5, 'sn333', 32) union
(select 103, '2023-06-13 11:07:07', 5, 'sn333', 32) union
(select 101, '2023-06-13 12:05:05', 5, 'sn333', 32) union
(select 103, '2023-06-13 12:07:07', 5, 'sn333', 32);


