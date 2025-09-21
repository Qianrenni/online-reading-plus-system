
# 将老版的reading数据库中的数据导入到新版的reading_plus数据库中
# insert into reading_plus.book(id, name, author, cover, description, category, tags, total_chapter, created_at)
# select b.book_id,b.title,b.author,b.cover_image,b.description,b.category,'',b.total_number,created_at
# from reading.books as b

select t.title,t.book_id,t.sort_order from reading_plus.book_chapter as t where t.book_id =3