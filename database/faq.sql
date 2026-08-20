CREATE TABLE faq(
	question_id INT PRIMARY KEY AUTO_INCREMENT,
	question VARCHAR(500),
	answer VARCHAR(500)
);

INSERT INTO faq (question,answer) 
VALUES 
(
"How long does delivery take?",
"Standard delivery usually takes 2 to 5 business days."
),
(
"Can I cancel my order?",
"Orders can be cancelled before they are shipped."
),
(
"What is your return policy?",
"Products can be returned within 14 days of delivery if they meet the return conditions."
),
(
"Which payment methods do you accept?",
"We accept credit cards, debit cards, and supported digital payment methods."
),
(
"How can I track my order?",
"You can track your order using the tracking number provided after your order has been shipped."
),
(
"Can I change my shipping address after placing an order?",
"The shipping address can only be changed before the order has been shipped."
),
(
"What should I do if my order arrives damaged?",
"Contact customer support and provide details about the damaged product so the issue can be reviewed."
),
(
"Do you offer international shipping?",
"International shipping is available only for supported countries and regions."
),
(
"How long does it take to receive a refund?",
"Approved refunds are usually processed within 5 to 10 business days."
),
(
"Can I exchange a product instead of returning it?",
"Eligible products can be exchanged according to the store's exchange conditions and product availability."
);

select * from faq;
