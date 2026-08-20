CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,

    customer_id INT NOT NULL,

    status VARCHAR(50) NOT NULL,

    total_price DECIMAL(10, 2) NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    shipped_at DATETIME NULL,

    delivered_at DATETIME NULL,

    tracking_number VARCHAR(100) NULL,

    carrier VARCHAR(100) NULL
);

INSERT INTO orders (
    customer_id,
    status,
    total_price,
    created_at,
    shipped_at,
    delivered_at,
    tracking_number,
    carrier
)
VALUES
(
    14,
    'shipped',
    899.99,
    '2026-08-17 14:30:00',
    '2026-08-18 10:15:00',
    NULL,
    'TRK938281',
    'Aras Kargo'
),
(
    14,
    'processing',
    249.50,
    '2026-08-19 09:20:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    22,
    'delivered',
    1299.00,
    '2026-08-10 11:00:00',
    '2026-08-11 08:40:00',
    '2026-08-13 16:25:00',
    'YK5548129',
    'Yurtiçi Kargo'
);

INSERT INTO orders (
    customer_id,
    status,
    total_price,
    created_at,
    shipped_at,
    delivered_at,
    tracking_number,
    carrier
)
VALUES
(
    5,
    'processing',
    179.90,
    '2026-08-20 08:15:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    31,
    'shipped',
    549.75,
    '2026-08-16 13:40:00',
    '2026-08-17 09:25:00',
    NULL,
    'ARS260817001',
    'Aras Kargo'
),
(
    8,
    'delivered',
    84.50,
    '2026-08-09 10:05:00',
    '2026-08-10 08:30:00',
    '2026-08-12 15:45:00',
    'YK260810002',
    'Yurtiçi Kargo'
),
(
    47,
    'processing',
    1249.99,
    '2026-08-19 17:55:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    19,
    'delivered',
    329.00,
    '2026-08-06 12:20:00',
    '2026-08-07 11:10:00',
    '2026-08-09 14:35:00',
    'MNG260807003',
    'MNG Kargo'
),
(
    26,
    'shipped',
    715.40,
    '2026-08-18 09:45:00',
    '2026-08-19 07:50:00',
    NULL,
    'SRT260819004',
    'Sürat Kargo'
),
(
    11,
    'processing',
    95.25,
    '2026-08-20 10:30:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    33,
    'delivered',
    2089.90,
    '2026-08-01 16:10:00',
    '2026-08-02 09:05:00',
    '2026-08-05 13:20:00',
    'PTT260802005',
    'PTT Kargo'
),
(
    52,
    'shipped',
    439.80,
    '2026-08-15 11:35:00',
    '2026-08-16 08:15:00',
    NULL,
    'UPS260816006',
    'UPS Türkiye'
),
(
    6,
    'processing',
    659.00,
    '2026-08-18 18:25:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    41,
    'delivered',
    149.99,
    '2026-07-29 14:50:00',
    '2026-07-30 10:40:00',
    '2026-08-01 12:05:00',
    'ARS260730007',
    'Aras Kargo'
),
(
    17,
    'shipped',
    899.50,
    '2026-08-17 08:55:00',
    '2026-08-18 07:35:00',
    NULL,
    'YK260818008',
    'Yurtiçi Kargo'
),
(
    28,
    'processing',
    275.60,
    '2026-08-19 12:45:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    44,
    'delivered',
    1099.00,
    '2026-08-11 09:15:00',
    '2026-08-12 08:20:00',
    '2026-08-14 17:10:00',
    'MNG260812009',
    'MNG Kargo'
),
(
    2,
    'shipped',
    59.90,
    '2026-08-14 15:30:00',
    '2026-08-15 10:05:00',
    NULL,
    'SRT260815010',
    'Sürat Kargo'
),
(
    36,
    'processing',
    1899.95,
    '2026-08-20 07:40:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    23,
    'delivered',
    480.00,
    '2026-08-04 13:25:00',
    '2026-08-05 09:50:00',
    '2026-08-07 11:30:00',
    'PTT260805011',
    'PTT Kargo'
),
(
    49,
    'shipped',
    134.75,
    '2026-08-16 19:05:00',
    '2026-08-17 12:15:00',
    NULL,
    'UPS260817012',
    'UPS Türkiye'
),
(
    13,
    'processing',
    749.20,
    '2026-08-18 16:35:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    55,
    'delivered',
    999.99,
    '2026-08-07 08:10:00',
    '2026-08-08 07:45:00',
    '2026-08-10 16:55:00',
    'ARS260808013',
    'Aras Kargo'
),
(
    30,
    'shipped',
    365.50,
    '2026-08-18 11:50:00',
    '2026-08-19 09:10:00',
    NULL,
    'YK260819014',
    'Yurtiçi Kargo'
),
(
    4,
    'processing',
    219.00,
    '2026-08-19 20:05:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    38,
    'delivered',
    1549.45,
    '2026-08-02 10:40:00',
    '2026-08-03 08:55:00',
    '2026-08-06 14:15:00',
    'MNG260803015',
    'MNG Kargo'
),
(
    21,
    'shipped',
    289.30,
    '2026-08-13 17:20:00',
    '2026-08-14 11:25:00',
    NULL,
    'SRT260814016',
    'Sürat Kargo'
),
(
    46,
    'processing',
    529.99,
    '2026-08-20 09:05:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    16,
    'delivered',
    639.90,
    '2026-08-12 14:05:00',
    '2026-08-13 10:35:00',
    '2026-08-15 12:50:00',
    'PTT260813017',
    'PTT Kargo'
),
(
    58,
    'shipped',
    1199.00,
    '2026-08-17 15:45:00',
    '2026-08-18 13:05:00',
    NULL,
    'UPS260818018',
    'UPS Türkiye'
),
(
    25,
    'processing',
    410.80,
    '2026-08-19 14:30:00',
    NULL,
    NULL,
    NULL,
    NULL
),
(
    43,
    'delivered',
    779.25,
    '2026-08-05 11:55:00',
    '2026-08-06 09:30:00',
    '2026-08-08 18:05:00',
    'ARS260806019',
    'Aras Kargo'
),
(
    10,
    'shipped',
    199.95,
    '2026-08-18 07:25:00',
    '2026-08-19 06:50:00',
    NULL,
    'YK260819020',
    'Yurtiçi Kargo'
);

select * from orders;
