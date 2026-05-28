import random
from datetime import datetime
from getpass import getpass
from supabase import create_client


# 전역 변수로 관리할 로컬 주문 캐시
local_order_history = []

# 실제 구매 가능 재고가 이 수량 이하가 되면 경고를 보여줍니다.
LOW_STOCK_THRESHOLD = 99


def connect_supabase():
    url = input("Supabase URL: ").strip()
    anon_key = getpass("Supabase anon key: ").strip()

    client = create_client(url, anon_key)
    print("Supabase 연결 완료")
    return client


# Supabase 연결 초기화
supabase = connect_supabase()


def get_stock_status_text(stock):
    if stock <= 0:
        return "품절"

    if stock <= LOW_STOCK_THRESHOLD:
        return "품절 임박"

    return "재고 충분"


def get_session_purchased_quantity(product_id):
    purchased_quantity = 0

    for order in local_order_history:
        for item in order["items"]:
            if item["product_id"] == product_id:
                purchased_quantity += item["quantity"]

    return purchased_quantity


def show_products():
    print("\n=== 판매 중인 상품 목록 (재고 포함) ===")
    try:
        # edu_shopping 커스텀 스키마를 직접 조회합니다.
        res = (
            supabase
            .schema("edu_shopping")
            .table("products")
            .select("product_id, product_name, list_price, status, inventory(quantity)")
            .eq("status", "ACTIVE")
            .execute()
        )

        products = res.data

        if not products:
            print("현재 등록된 상품이 없습니다.")
            return False

        print(f"{'ID':<5} | {'상품명':<22} | {'가격':<10} | {'구매가능':<8} | {'재고상태':<8} | {'상태':<5}")
        print("-" * 85)

        for p in products:
            inv_data = p.get("inventory")
            stock = inv_data["quantity"] if inv_data else 0
            stock_status = get_stock_status_text(stock)

            print(
                f"{p['product_id']:<5} | "
                f"{p['product_name']:<20} | "
                f"{p['list_price']:<10} | "
                f"{stock:<8} | "
                f"{stock_status:<8} | "
                f"{p['status']:<5}"
            )
        return True

    except Exception as e:
        print(f"상품 목록을 불러오는 중 오류 발생: {e}")
        return False


def show_inventory_status():
    print("\n=== 현재 재고 현황 (실제 구매 가능 재고) ===")
    try:
        res = (
            supabase
            .schema("edu_shopping")
            .table("products")
            .select("product_id, product_name, list_price, status, inventory(quantity)")
            .order("product_id")
            .execute()
        )

        products = res.data

        if not products:
            print("현재 등록된 상품이 없습니다.")
            return

        print(
            f"{'ID':<5} | {'상품명':<22} | {'현재 구매가능':<12} | "
            f"{'현재 세션 구매':<12} | {'주문 전 추정':<12} | {'재고상태':<8}"
        )
        print("-" * 95)

        for product in products:
            inv_data = product.get("inventory")
            current_stock = inv_data["quantity"] if inv_data else 0
            current_stock = max(current_stock, 0)

            purchased_quantity = get_session_purchased_quantity(product["product_id"])
            estimated_before_order_stock = current_stock + purchased_quantity
            stock_status = get_stock_status_text(current_stock)

            print(
                f"{product['product_id']:<5} | "
                f"{product['product_name']:<20} | "
                f"{current_stock:<12} | "
                f"{purchased_quantity:<12} | "
                f"{estimated_before_order_stock:<12} | "
                f"{stock_status:<8}"
            )

        print("\n※ 현재 구매가능 재고는 inventory.quantity 기준이며, 이미 구매 완료된 수량이 차감된 값입니다.")
        print("※ 현재 세션 구매 수량은 이 프로그램을 실행한 뒤 주문한 수량만 집계합니다.")

    except Exception as e:
        print(f"재고 현황을 불러오는 중 오류 발생: {e}")


def select_payment_method():
    payment_methods = {
        "1": "CARD",
        "2": "BANK_TRANSFER",
        "3": "POINT",
    }

    while True:
        print("\n=== 결제 수단 선택 ===")
        print("1. CARD")
        print("2. BANK_TRANSFER")
        print("3. POINT")

        choice = input("결제 수단을 선택하세요: ").strip()

        if choice in payment_methods:
            return payment_methods[choice]

        print("❌ 1~3 중에서 결제 수단을 선택해주세요.")


def generate_unique_id(table_name, column_name):
    while True:
        new_id = random.randint(100000, 999999)

        res = (
            supabase
            .schema("edu_shopping")
            .table(table_name)
            .select(column_name)
            .eq(column_name, new_id)
            .execute()
        )

        if not res.data:
            return new_id


def get_product_with_stock(product_id):
    p_res = (
        supabase
        .schema("edu_shopping")
        .table("products")
        .select("product_id, list_price, product_name, status, inventory(quantity)")
        .eq("product_id", product_id)
        .single()
        .execute()
    )

    product_data = p_res.data

    if not product_data:
        return None

    inv_data = product_data.get("inventory")
    product_data["stock_quantity"] = inv_data["quantity"] if inv_data else 0
    return product_data


def get_cart_quantity(cart_items, product_id):
    total_quantity = 0

    for item in cart_items:
        if item["product_id"] == product_id:
            total_quantity += item["quantity"]

    return total_quantity


def add_items_to_cart():
    cart_items = []

    while True:
        if not show_products():
            return cart_items

        product_id_input = input("\n구매할 상품 ID를 입력하세요 (0: 상품 선택 종료): ").strip()

        if product_id_input == "0":
            return cart_items

        quantity_input = input("구매할 수량을 입력하세요: ").strip()

        if not (product_id_input.isdigit() and quantity_input.isdigit()):
            print("❌ 오류: 상품 ID와 수량은 숫자로만 입력해야 합니다.")
            continue

        p_id = int(product_id_input)
        qty = int(quantity_input)

        if qty <= 0:
            print("❌ 오류: 수량은 1개 이상이어야 합니다.")
            continue

        try:
            product_data = get_product_with_stock(p_id)

            if not product_data:
                print("❌ 오류: 존재하지 않는 상품 ID입니다.")
                continue

            if product_data["status"] != "ACTIVE":
                print("❌ 오류: 판매 중인 상품만 주문할 수 있습니다.")
                continue

            already_selected_qty = get_cart_quantity(cart_items, p_id)
            current_stock = product_data["stock_quantity"]
            remaining_after_cart = current_stock - already_selected_qty - qty

            if remaining_after_cart < 0:
                print(
                    f"❌ 주문 실패: 재고가 부족합니다. "
                    f"(현재 재고: {current_stock}개, 이미 선택한 수량: {already_selected_qty}개)"
                )
                continue

            cart_items.append(
                {
                    "product_id": p_id,
                    "product_name": product_data["product_name"],
                    "quantity": qty,
                    "unit_price": product_data["list_price"],
                    "discount_rate": 0.0,
                }
            )

            print(f"✅ 장바구니 추가: {product_data['product_name']} {qty}개")
            print(f"선택 후 실제 구매 가능 재고: {remaining_after_cart}개")

            if 0 < remaining_after_cart <= LOW_STOCK_THRESHOLD:
                print("⚠️ 품절 임박: 해당 상품의 남은 재고가 99개 이하입니다.")
            elif remaining_after_cart == 0:
                print("⚠️ 품절: 이번 선택 후 남은 재고가 0개입니다.")

            more = input("상품을 추가로 구매하시겠습니까? (y/n): ").strip().lower()
            if more != "y":
                return cart_items

        except Exception as e:
            print(f"❌ 상품 조회 중 오류 발생: {e}")
            continue


def place_order():
    print("\n=== 신규 고객 정보 및 주문 등록 ===")

    # 1. 고객 ID 중복 검사 및 입력 루프
    while True:
        customer_id_input = input("사용할 고객 ID를 입력하세요 (숫자): ").strip()
        if not customer_id_input.isdigit():
            print("❌ 올바른 숫자로만 입력해주세요.")
            continue

        customer_id = int(customer_id_input)

        try:
            check_res = (
                supabase
                .schema("edu_shopping")
                .table("customers")
                .select("customer_id")
                .eq("customer_id", customer_id)
                .execute()
            )

            if check_res.data:
                print(f"⚠️ 고객 ID {customer_id}는 이미 존재합니다. 다른 숫자를 입력해 주세요.")
                print("-" * 40)
            else:
                break

        except Exception as e:
            print(f"❌ 고객 ID 조회 중 오류 발생: {e}")
            return

    # 2. 나머지 고객 정보 입력 받기
    customer_name = input("고객 이름을 입력하세요: ").strip()
    customer_phone = input("전화번호를 입력하세요 (예: 010-XXXX-XXXX): ").strip()
    customer_email = input("이메일을 입력하세요 (선택사항, 엔터 가능): ").strip()

    if not customer_name or not customer_phone:
        print("❌ 오류: 고객 이름과 전화번호는 필수 입력 항목입니다.")
        return

    payment_method = select_payment_method()
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 3. 상품을 1개 이상 선택합니다. 선택 후 바로 추가 구매 여부를 묻습니다.
    cart_items = add_items_to_cart()

    if not cart_items:
        print("❌ 선택된 상품이 없어 주문을 취소합니다.")
        return

    try:
        # [단계 1] customers 테이블에 신규 고객 정보 삽입
        customer_record = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "email": customer_email if customer_email else None,
            "phone": customer_phone,
            "signup_date": current_date,
        }

        print("\n고객 정보 등록 중...")
        supabase.schema("edu_shopping").table("customers").insert(customer_record).execute()

        # [단계 2] orders 테이블에 주문 마스터 생성
        order_id = generate_unique_id("orders", "order_id")
        order_record = {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": current_date,
            "order_status": "PAID",
            "payment_method": payment_method,
        }

        print("주문 정보 등록 중...")
        supabase.schema("edu_shopping").table("orders").insert(order_record).execute()

        saved_items = []
        total_order_price = 0

        # [단계 3] 선택한 상품 수만큼 order_items 저장 및 inventory 차감
        for cart_item in cart_items:
            p_id = cart_item["product_id"]
            qty = cart_item["quantity"]

            product_data = get_product_with_stock(p_id)
            if not product_data:
                print(f"❌ 오류: 상품 ID {p_id}를 다시 조회하지 못했습니다.")
                return

            current_stock = product_data["stock_quantity"]

            if current_stock < qty:
                print(f"❌ 주문 실패: {product_data['product_name']} 재고가 부족합니다. 현재 재고: {current_stock}개")
                return

            order_item_id = generate_unique_id("order_items", "order_item_id")
            discount_rate = cart_item["discount_rate"]

            item_record = {
                "order_item_id": order_item_id,
                "order_id": order_id,
                "product_id": p_id,
                "quantity": qty,
                "unit_price": cart_item["unit_price"],
                "discount_rate": discount_rate,
            }

            supabase.schema("edu_shopping").table("order_items").insert(item_record).execute()

            new_stock = current_stock - qty

            if new_stock < 0:
                print(f"❌ 주문 실패: {product_data['product_name']} 재고가 0보다 작아질 수 없습니다.")
                return

            supabase.schema("edu_shopping").table("inventory").update(
                {"quantity": new_stock}
            ).eq("product_id", p_id).execute()

            item_total_price = qty * cart_item["unit_price"] * (1 - discount_rate)
            total_order_price += item_total_price

            saved_items.append(
                {
                    "product_id": p_id,
                    "product_name": cart_item["product_name"],
                    "quantity": qty,
                    "unit_price": cart_item["unit_price"],
                    "discount_rate": discount_rate,
                    "total_price": item_total_price,
                    "remaining_stock": new_stock,
                    "stock_status": get_stock_status_text(new_stock),
                }
            )

        print(f"\n🎉 {customer_name} 회원님의 주문이 성공적으로 완료되었습니다!")
        print(f"주문번호: {order_id}")
        print(f"결제수단: {payment_method}")
        print(f"총 결제금액: {int(total_order_price)}원")

        for item in saved_items:
            print(
                f"- 주문 상품: {item['product_name']} / "
                f"수량: {item['quantity']}개 / "
                f"남은 재고: {item['remaining_stock']}개 / "
                f"재고상태: {item['stock_status']} / "
                f"금액: {int(item['total_price'])}원"
            )

            if item["stock_status"] == "품절 임박":
                print("  ⚠️ 품절 임박: 이 상품의 남은 재고가 99개 이하입니다.")
            elif item["stock_status"] == "품절":
                print("  ⚠️ 품절: 이 상품의 남은 재고가 없습니다.")

        # 로컬 캐시에 주문 단위로 기록 저장
        local_order_history.append(
            {
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "payment_method": payment_method,
                "total_price": total_order_price,
                "items": saved_items,
            }
        )

    except Exception as e:
        print(f"❌ 처리 중 오류가 발생했습니다: {e}")
        print("힌트: 중복된 전화번호나 이메일이 입력되었는지 확인하세요.")


def show_local_orders():
    if not local_order_history:
        print("\n현재 세션에서 주문한 내역이 없습니다.")
        return

    print("\n=== 현재 세션 주문 내역 (로컬) ===")
    for idx, ord in enumerate(local_order_history, start=1):
        print("-" * 80)
        print(f"[{idx}] 주문번호: {ord['order_id']}")
        print(f"회원명: {ord['customer_name']} | 연락처: {ord['customer_phone']}")
        print(f"결제수단: {ord['payment_method']} | 총 금액: {int(ord['total_price'])}원")
        print("주문 상품:")

        for item in ord["items"]:
            print(
                f"  - 상품명: {item['product_name']} | "
                f"수량: {item['quantity']}개 | "
                f"남은 재고: {item['remaining_stock']}개 | "
                f"재고상태: {item['stock_status']} | "
                f"금액: {int(item['total_price'])}원"
            )


def print_menu():
    print("\n=== 미니 이커머스 시스템 ===")
    print("1. 상품 목록 보기 (재고 포함)")
    print("2. 상품 주문하기 (신규 회원 등록 포함)")
    print("3. 최근 주문 내역 보기 (로컬 캐시)")
    print("4. 현재 재고 현황 보기 (실제 구매 가능 재고)")
    print("5. 종료")


def main():
    while True:
        print_menu()
        menu = input("메뉴 Choice: ").strip()

        if menu == "1":
            show_products()
        elif menu == "2":
            place_order()
        elif menu == "3":
            show_local_orders()
        elif menu == "4":
            show_inventory_status()
        elif menu == "5":
            print("프로그램을 종료합니다.")
            break
        else:
            print("1~5 중에서 올바른 번호를 선택해주세요.")


if __name__ == "__main__":
    main()
