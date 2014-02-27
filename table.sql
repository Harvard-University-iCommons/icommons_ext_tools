alter table qualtrics.qualtrics_access_list
add (expiration_date date default sysdate+90 not null);
