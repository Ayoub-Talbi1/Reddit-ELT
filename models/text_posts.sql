SELECT id, 
   title, 
   author,
   score,
   upvote_ratio,
   num_comments, 
   posting_time,
   url,
   posting_time::date as utc_date,
   posting_time::time as utc_time
FROM mydb.public.reddit