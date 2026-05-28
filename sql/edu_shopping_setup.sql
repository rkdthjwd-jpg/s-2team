-- ============================================================
-- edu_shopping 실습용 전체 SQL
-- 1. 스키마 초기화
-- 2. 테이블 생성
-- 3. 샘플 데이터 삽입
-- 4. 상품 조회 View 생성
-- 5. 주문 처리 RPC 함수 생성
-- 6. Supabase API 권한 부여
-- ============================================================

DROP SCHEMA IF EXISTS edu_shopping CASCADE;

CREATE SCHEMA edu_shopping;


-- ============================================================
-- 1. customers
-- ============================================================

CREATE TABLE edu_shopping.customers (
    customer_id     INTEGER PRIMARY KEY,
    customer_name   VARCHAR(30) NOT NULL,
    email           VARCHAR(50) UNIQUE,
    phone           TEXT UNIQUE,
    signup_date     DATE DEFAULT CURRENT_DATE
);


-- ============================================================
-- 2. product_categories
-- ============================================================

CREATE TABLE edu_shopping.product_categories (
    category_id     INTEGER PRIMARY KEY,
    category_name   TEXT NOT NULL
);


-- ============================================================
-- 3. products
-- ============================================================

CREATE TABLE edu_shopping.products (
    product_id      INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category_id     INTEGER NOT NULL,
    list_price      NUMERIC NOT NULL,
    status          TEXT NOT NULL,

    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id)
        REFERENCES edu_shopping.product_categories(category_id)
);


-- ============================================================
-- 4. orders
-- ============================================================

CREATE TABLE edu_shopping.orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    order_date      DATE NOT NULL,
    order_status    TEXT NOT NULL,
    payment_method  TEXT NOT NULL,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES edu_shopping.customers(customer_id)
);


-- ============================================================
-- 5. order_items
-- ============================================================

CREATE TABLE edu_shopping.order_items (
    order_item_id   INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC NOT NULL,
    discount_rate   NUMERIC NOT NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES edu_shopping.orders(order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES edu_shopping.products(product_id),

    CONSTRAINT chk_order_items_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_order_items_discount_rate
        CHECK (discount_rate >= 0 AND discount_rate <= 1)
);


-- ============================================================
-- 6. inventory
-- ============================================================

CREATE TABLE edu_shopping.inventory (
    product_id      INTEGER PRIMARY KEY,
    quantity        INTEGER NOT NULL,

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES edu_shopping.products(product_id),

    CONSTRAINT chk_inventory_quantity
        CHECK (quantity >= 0)
);


-- ============================================================
-- 샘플 데이터 삽입
-- ============================================================

BEGIN;

-- product_categories
INSERT INTO edu_shopping.product_categories
(category_id, category_name)
VALUES
(1, '상의'),
(2, '하의'),
(3, '아우터'),
(4, '원피스');


-- customers
INSERT INTO edu_shopping.customers
(customer_id, customer_name, email, phone, signup_date)
VALUES
(1, '김민준', 'minjun.kim@example.com', '010-1000-0001', DATE '2026-01-03'),
(2, '이서연', 'seoyeon.lee@example.com', '010-1000-0002', DATE '2026-01-05'),
(3, '박지훈', 'jihoon.park@example.com', '010-1000-0003', DATE '2026-01-07'),
(4, '최하은', 'haeun.choi@example.com', '010-1000-0004', DATE '2026-01-10'),
(5, '정도윤', 'doyoon.jung@example.com', '010-1000-0005', DATE '2026-01-12'),
(6, '강서아', 'seoa.kang@example.com', '010-1000-0006', DATE '2026-01-15'),
(7, '윤현우', 'hyunwoo.yoon@example.com', '010-1000-0007', DATE '2026-01-18'),
(8, '장유진', 'yujin.jang@example.com', '010-1000-0008', DATE '2026-01-21'),
(9, '임지아', 'jia.lim@example.com', '010-1000-0009', DATE '2026-01-25'),
(10, '한도현', 'dohyun.han@example.com', '010-1000-0010', DATE '2026-01-28');


-- products
INSERT INTO edu_shopping.products
(product_id, product_name, category_id, list_price, status)
VALUES
(101, '베이직 코튼 티셔츠', 1, 19000, 'ACTIVE'),
(102, '오버핏 린넨 셔츠', 1, 39000, 'ACTIVE'),
(103, '스웨트 맨투맨', 1, 45000, 'ACTIVE'),
(104, '후드 집업', 3, 59000, 'ACTIVE'),
(105, '데님 팬츠', 2, 49000, 'ACTIVE'),
(106, '와이드 슬랙스', 2, 54000, 'ACTIVE'),
(107, '치노 팬츠', 2, 47000, 'ACTIVE'),
(108, '트렌치 코트', 3, 129000, 'ACTIVE'),
(109, '울 가디건', 3, 89000, 'ACTIVE'),
(110, '니트 원피스', 4, 69000, 'ACTIVE');


-- inventory
INSERT INTO edu_shopping.inventory
(product_id, quantity)
VALUES
(101, 850),
(102, 620),
(103, 540),
(104, 430),
(105, 760),
(106, 390),
(107, 580),
(108, 210),
(109, 330),
(110, 470);


-- orders
INSERT INTO edu_shopping.orders
(order_id, customer_id, order_date, order_status, payment_method)
VALUES
(1001, 1, DATE '2026-02-01', 'PAID', 'CARD'),
(1002, 2, DATE '2026-02-02', 'PAID', 'CARD'),
(1003, 3, DATE '2026-02-03', 'SHIPPED', 'BANK_TRANSFER'),
(1004, 4, DATE '2026-02-04', 'PAID', 'CARD'),
(1005, 5, DATE '2026-02-05', 'DELIVERED', 'POINT'),
(1006, 6, DATE '2026-02-06', 'PAID', 'CARD'),
(1007, 7, DATE '2026-02-07', 'SHIPPED', 'BANK_TRANSFER'),
(1008, 8, DATE '2026-02-08', 'PAID', 'CARD'),
(1009, 9, DATE '2026-02-09', 'DELIVERED', 'CARD'),
(1010, 10, DATE '2026-02-10', 'PAID', 'BANK_TRANSFER'),
(1011, 1, DATE '2026-02-11', 'SHIPPED', 'CARD'),
(1012, 3, DATE '2026-02-12', 'PAID', 'POINT');


-- order_items
INSERT INTO edu_shopping.order_items
(order_item_id, order_id, product_id, quantity, unit_price, discount_rate)
VALUES
(1, 1001, 101, 120, 19000, 0.00),
(2, 1001, 105, 150, 49000, 0.05),
(3, 1002, 102, 110, 39000, 0.00),
(4, 1002, 106, 130, 54000, 0.10),
(5, 1003, 103, 180, 45000, 0.05),
(6, 1003, 107, 140, 47000, 0.00),
(7, 1004, 104, 100, 59000, 0.00),
(8, 1004, 108, 105, 129000, 0.15),
(9, 1005, 109, 125, 89000, 0.10),
(10, 1005, 110, 160, 69000, 0.05),
(11, 1006, 101, 200, 19000, 0.00),
(12, 1006, 102, 170, 39000, 0.05),
(13, 1007, 105, 220, 49000, 0.10),
(14, 1007, 106, 115, 54000, 0.00),
(15, 1008, 107, 190, 47000, 0.05),
(16, 1008, 103, 135, 45000, 0.00),
(17, 1009, 108, 100, 129000, 0.20),
(18, 1010, 109, 145, 89000, 0.10),
(19, 1011, 104, 155, 59000, 0.05),
(20, 1012, 110, 175, 69000, 0.00);

COMMIT;


-- ============================================================
-- 상품 + 재고 조회용 View
-- Python 메뉴 1번에서 사용
-- ============================================================

CREATE OR REPLACE VIEW public.v_edu_shopping_active_products AS
SELECT
    p.product_id,
    p.product_name,
    p.list_price,
    p.status,
    c.category_name,
    i.quantity AS stock_quantity
FROM edu_shopping.products p
JOIN edu_shopping.product_categories c
    ON p.category_id = c.category_id
LEFT JOIN edu_shopping.inventory i
    ON p.product_id = i.product_id
WHERE p.status = 'ACTIVE';


-- ============================================================
-- 주문 ID / 주문상세 ID 자동 생성을 위한 Sequence
-- Python에서 random ID를 만들지 않도록 DB에서 관리
-- ============================================================

CREATE SEQUENCE IF NOT EXISTS edu_shopping.order_id_seq;

SELECT setval(
    'edu_shopping.order_id_seq',
    GREATEST(
        COALESCE((SELECT MAX(order_id) FROM edu_shopping.orders), 0) + 1,
        200000
    ),
    false
);

CREATE SEQUENCE IF NOT EXISTS edu_shopping.order_item_id_seq;

SELECT setval(
    'edu_shopping.order_item_id_seq',
    GREATEST(
        COALESCE((SELECT MAX(order_item_id) FROM edu_shopping.order_items), 0) + 1,
        200000
    ),
    false
);


-- ============================================================
-- 신규 고객 등록 + 주문 생성 + 주문상세 생성 + 재고 차감 RPC 함수
-- Python 메뉴 2번에서 사용
-- ============================================================

CREATE OR REPLACE FUNCTION public.place_edu_shopping_order(
    p_customer_id INTEGER,
    p_customer_name TEXT,
    p_email TEXT,
    p_phone TEXT,
    p_product_id INTEGER,
    p_quantity INTEGER,
    p_payment_method TEXT DEFAULT 'CARD'
)
RETURNS TABLE (
    order_id INTEGER,
    order_item_id INTEGER,
    product_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    unit_price NUMERIC,
    total_price NUMERIC,
    remaining_stock INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = edu_shopping, public
AS $$
DECLARE
    v_product_name TEXT;
    v_unit_price NUMERIC;
    v_status TEXT;
    v_stock INTEGER;
    v_order_id INTEGER;
    v_order_item_id INTEGER;
BEGIN
    -- 1. 기본 입력 검증
    IF p_customer_id IS NULL THEN
        RAISE EXCEPTION '고객 ID는 필수입니다.';
    END IF;

    IF p_customer_name IS NULL OR LENGTH(TRIM(p_customer_name)) = 0 THEN
        RAISE EXCEPTION '고객 이름은 필수입니다.';
    END IF;

    IF p_phone IS NULL OR LENGTH(TRIM(p_phone)) = 0 THEN
        RAISE EXCEPTION '전화번호는 필수입니다.';
    END IF;

    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        RAISE EXCEPTION '구매 수량은 1개 이상이어야 합니다.';
    END IF;

    -- 2. 고객 ID 중복 체크
    IF EXISTS (
        SELECT 1
        FROM edu_shopping.customers
        WHERE customer_id = p_customer_id
    ) THEN
        RAISE EXCEPTION '이미 존재하는 고객 ID입니다: %', p_customer_id;
    END IF;

    -- 3. 전화번호 중복 체크
    IF EXISTS (
        SELECT 1
        FROM edu_shopping.customers
        WHERE phone = p_phone
    ) THEN
        RAISE EXCEPTION '이미 등록된 전화번호입니다: %', p_phone;
    END IF;

    -- 4. 이메일 중복 체크
    IF p_email IS NOT NULL AND LENGTH(TRIM(p_email)) > 0 THEN
        IF EXISTS (
            SELECT 1
            FROM edu_shopping.customers
            WHERE email = p_email
        ) THEN
            RAISE EXCEPTION '이미 등록된 이메일입니다: %', p_email;
        END IF;
    END IF;

    -- 5. 상품 조회
    SELECT
        product_name,
        list_price,
        status
    INTO
        v_product_name,
        v_unit_price,
        v_status
    FROM edu_shopping.products
    WHERE product_id = p_product_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION '존재하지 않는 상품 ID입니다: %', p_product_id;
    END IF;

    IF v_status <> 'ACTIVE' THEN
        RAISE EXCEPTION '판매 중인 상품이 아닙니다. 현재 상태: %', v_status;
    END IF;

    -- 6. 재고 조회 및 잠금
    SELECT
        quantity
    INTO
        v_stock
    FROM edu_shopping.inventory
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION '해당 상품의 재고 정보가 없습니다: %', p_product_id;
    END IF;

    IF v_stock < p_quantity THEN
        RAISE EXCEPTION '재고가 부족합니다. 현재 재고: %, 요청 수량: %', v_stock, p_quantity;
    END IF;

    -- 7. 고객 생성
    INSERT INTO edu_shopping.customers (
        customer_id,
        customer_name,
        email,
        phone,
        signup_date
    )
    VALUES (
        p_customer_id,
        p_customer_name,
        NULLIF(TRIM(p_email), ''),
        p_phone,
        CURRENT_DATE
    );

    -- 8. 주문 생성
    v_order_id := nextval('edu_shopping.order_id_seq')::INTEGER;

    INSERT INTO edu_shopping.orders (
        order_id,
        customer_id,
        order_date,
        order_status,
        payment_method
    )
    VALUES (
        v_order_id,
        p_customer_id,
        CURRENT_DATE,
        'PAID',
        p_payment_method
    );

    -- 9. 주문상세 생성
    v_order_item_id := nextval('edu_shopping.order_item_id_seq')::INTEGER;

    INSERT INTO edu_shopping.order_items (
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount_rate
    )
    VALUES (
        v_order_item_id,
        v_order_id,
        p_product_id,
        p_quantity,
        v_unit_price,
        0
    );

    -- 10. 재고 차감
    UPDATE edu_shopping.inventory
    SET quantity = quantity - p_quantity
    WHERE product_id = p_product_id;

    -- 11. 결과 반환
    RETURN QUERY
    SELECT
        v_order_id AS order_id,
        v_order_item_id AS order_item_id,
        p_product_id AS product_id,
        v_product_name AS product_name,
        p_quantity AS quantity,
        v_unit_price AS unit_price,
        p_quantity * v_unit_price AS total_price,
        v_stock - p_quantity AS remaining_stock;
END;
$$;


-- ============================================================
-- Supabase API 권한
-- 실습용. RLS를 켜지 않은 기준.
-- ============================================================

GRANT USAGE ON SCHEMA edu_shopping TO anon, authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA edu_shopping
TO anon, authenticated;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA edu_shopping
TO anon, authenticated;

GRANT SELECT
ON public.v_edu_shopping_active_products
TO anon, authenticated;

GRANT EXECUTE ON FUNCTION public.place_edu_shopping_order(
    INTEGER,
    TEXT,
    TEXT,
    TEXT,
    INTEGER,
    INTEGER,
    TEXT
) TO anon, authenticated;


