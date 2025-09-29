
# 将老版的reading数据库中的数据导入到新版的reading_plus数据库中
# insert into reading_plus.book(id, name, author, cover, description, category, tags, total_chapter, created_at)
# select b.book_id,b.title,b.author,b.cover_image,b.description,b.category,'',b.total_number,created_at
# from reading.books as b
create database  if not exists reading_plus;

select t.title,t.sort_order from reading_plus.book_chapter as t
where  t.book_id =1;

select * from (
    SELECT
    content as content,
    ROW_NUMBER() OVER (ORDER BY sort_order) AS rn
FROM reading_plus.book_chapter
WHERE book_id = 1
 ) as cr
where cr.rn =1;

SELECT content,title
FROM reading_plus.book_chapter
WHERE book_id = 1
ORDER BY sort_order
LIMIT 1 OFFSET 2;

insert into reading_plus.user_reading_progress(user_id,book_id,last_chapter_id,last_position,last_read_at)
values  (1,1,1,0,now()),(1,2,1,0,now()),(1,3,1,0,now())
