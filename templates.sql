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



