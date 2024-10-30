SELECT
    c.id,
    ul.full_name as leaser_name,
    ut.full_name as taker_name,
    i.price_day,
    julianday(c.end_date) - julianday(c.start_date) AS rental_days,
    i.price_day * (julianday(c.end_date) - julianday(c.start_date)) AS total_price
FROM contract c
    JOIN item i ON c.item = i.id
    JOIN user ul  ON c.leaser = ul.id
    JOIN user ut ON c.taker = ut.id
WHERE total_price > 200
ORDER BY rental_days;
