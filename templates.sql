--drop table template_access_list;
--drop table template_accounts;
--drop table template_users;
--drop table templates;

CREATE TABLE template_access_list
   (  
    "SIS_ACCOUNT_ID" VARCHAR2(20 BYTE) NOT NULL ENABLE, 
    "TEMPLATE_ID" NUMBER(*,0) NOT NULL ENABLE, 
    "USER_ID" VARCHAR2(20 BYTE)
   ) ;

ALTER TABLE template_access_list ADD CONSTRAINT access_list_PK PRIMARY KEY ( "SIS_ACCOUNT_ID", "TEMPLATE_ID", "USER_ID" ) ;

CREATE TABLE template_accounts
   (  
    "SIS_ACCOUNT_ID" VARCHAR2(20 BYTE) NOT NULL, 
    "ACCOUNT_NAME" VARCHAR2(50 BYTE) NOT NULL, 
    "CAN_USE_WIZARD" CHAR(1 BYTE) DEFAULT 'N'
   ) ;

ALTER TABLE template_accounts ADD CONSTRAINT accounts_PK PRIMARY KEY ( "SIS_ACCOUNT_ID" ) ;

CREATE TABLE template_users
   (  
    "USER_ID" VARCHAR2(20 BYTE) NOT NULL ENABLE, 
    "SIS_ACCOUNT_ID" VARCHAR2(20 BYTE)
   );

ALTER TABLE template_users ADD CONSTRAINT users_PK PRIMARY KEY ( "USER_ID" ) ;

CREATE TABLE templates
   (  
    "TEMPLATE_ID" NUMBER(11,0) NOT NULL ENABLE, 
    "TEMPLATE_TERM" VARCHAR2(200 BYTE), 
    "TEMPLATE_TITLE" VARCHAR2(200 BYTE), 
    "CANVAS_COURSE_ID" NUMBER(11,0)
   );

ALTER TABLE templates ADD CONSTRAINT templates_PK PRIMARY KEY ( "TEMPLATE_ID" ) ;

CREATE SEQUENCE  templates_sq  MINVALUE 1 INCREMENT BY 1 START WITH 1 CACHE 20 ;

-- insert into templates values (templates_sq.nextval, 'Fall 2014', 'DCE / Fall 2014', 4580);
-- insert into templates values (templates_sq.nextval, 'Spring 2014', 'Harvard Extension School / Spring 2014', 4580);
-- insert into templates values (templates_sq.nextval, 'Full Year 2014', 'FAS Full Year 2014', 4580);
-- insert into templates values (templates_sq.nextval, 'Fall 2014', 'GSE / Fall 2014', 4580);
-- insert into templates values (templates_sq.nextval, 'Spring 2014', 'GSE / Spring 2014', 4580);
-- insert into templates values (templates_sq.nextval, 'Fall 2014', 'HLS / Fall 2014', 4580);
-- insert into template_accounts values('colgsag','colgsas',  'Y');
-- insert into template_accounts values('ext','Harvard Extension School',  'N');
-- insert into template_accounts values('hds','Harvard Design School',  'Y');
-- insert into template_accounts values('gse','gse',  'Y');
-- insert into template_accounts values('hls-berkman','hls-berkman',  'N');
-- insert into template_users values('20533064', 'ext');
-- insert into template_access_list values('ext',1,'20533064');

