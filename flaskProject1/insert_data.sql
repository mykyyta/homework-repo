-- Insert test users
INSERT INTO main.user (login, password, individual_number, full_name, contacts, photo) VALUES
('user1', 'password1', 123456789, 'John Doe', 'john@example.com', 'photo1.jpg'),
('user2', 'password2', 987654321, 'Jane Smith', 'jane@example.com', 'photo2.jpg'),
('user3', 'password3', 112233445, 'Alice Johnson', 'alice@example.com', 'photo3.jpg'),
('user4', 'password4', 556677889, 'Bob Brown', 'bob@example.com', 'photo4.jpg');

-- Insert test items
INSERT INTO main.item (name, description, owner, price_hour, price_day, price_week, price_month) VALUES
('Bicycle', 'A high-quality mountain bike', 1, 5.0, 20.0, 60.0, 200.0),
('Laptop', 'A powerful gaming laptop', 2, 2.0, 30.0, 100.0, 350.0),
('Camera', 'DSLR camera with 18-55mm lens', 1, 3.0, 15.0, 50.0, 150.0),
('Tent', '4-person camping tent', 3, 4.0, 10.0, 35.0, 120.0);

-- Insert test contracts
INSERT INTO main.contract (start_date, end_date, text, leaser, taker, item) VALUES
('2024-10-01', '2024-10-15', 'Lease agreement for Bicycle', 1, 2, 1),
('2024-10-05', '2024-10-12', 'Lease agreement for Laptop', 2, 3, 2),
('2024-10-10', '2024-10-20', 'Lease agreement for Tent', 3, 4, 4);

-- Insert test favorites
INSERT INTO main.favorite (user, favorite_item) VALUES
(1, 2),
(1, 3),
(2, 1),
(3, 4);

-- Insert test feedback
INSERT INTO main.feedback (contract, author, user, text, grade) VALUES
(1, 2, 1, 'Great experience with the bicycle!', 5),
(2, 3, 2, 'The laptop worked perfectly for my needs.', 4),
(3, 1, 3, 'The tent was easy to set up and very spacious.', 5);

-- Insert test search history
INSERT INTO main.search_history (user, search_text, timestamp) VALUES
(1, 'bicycle for rent', 1696137600),
(2, 'laptop rental options', 1696224000),
(3, 'best camping tents', 1696310400),
(4, 'high-quality cameras', 1696396800);