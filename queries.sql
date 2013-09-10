# Raw Fortune 500 (2013) People, Company_ID, Sequence & People Title

select b.seq_num, b.company_id, b.position, a.* from f500_person_object as a inner join (select a.seq_num, b.person_id, b.position, b.company_id from (select * from f500_company_year_link where year_id = "2013_new" and seq_num <= 500) as a inner join f500_person_company_link as b on a.company_id = b.company_id) as b on a.person_id = b.person_id;
