import os
from decimal import Decimal
from getpass import getpass
from typing import Any

from dotenv import load_dotenv
from supabase import create_client, Client


local_order_history: list[dict[str, Any]] = []


def connect_supabase() -> Client:
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not url:
        url = input("Supabase URL: ").strip()

    if not anon_key:
        anon_key = getpass("Supabase anon key: ").strip()

    if not url or not anon_key:
        raise ValueError("Supabase URL과 anon key가 필요합니다.")

    client = create_client(url, anon_key)
    print("✅ Supabase 연결 완료")
    return client


supabase = connect_supabase()


def format_money(value: Any) -> str:
    number = Decimal(str(value))
    return f"{int(number):,}원"


def show_products() -> bool:
    print("\n=== 판매 중인 상품 목록 ===")

    try:
        res = (
            supabase
            .table("v_edu_shopping_active_products")
            .select("*")
            .order("product_id")
            .execute()
        )

        products = res.data or []

        if not products:
            print("현재 판매 중인 상품이 없습니다.")
            return False

        print(f"{'ID':<6} | {'상품명':<20} | {'카테고리':<8} | {'가격':<12} | {'재고':<8}")
        print("-" * 75)

        for p in products:
            stock_quantity = p["stock_quantity"] if p["stock_quantity"] is not None else 0

            print(
                f"{p['product_id']:<6} | "
                f"{p['product_name']:<20} | "
                f"{p['category_name']:<8} | "
                f"{format_money(p['list_price']):<12} | "
                f"{stock_quantity:<8}"
            )

        return True

    except Exception as e:
        print(f"❌ 상품 목록 조회 실패: {e}")
        print("확인할 것: public.v_edu_shopping_active_products View 생성 여부, 권한 설정")
        return False


def input_positive_int(message: str) -> int | None:
    value = input(message).strip()

    if not value.isdigit():
        print("❌ 숫자로만 입력해주세요.")
        return None

    number = int(value)

    if number <= 0:
        print("❌ 1 이상의 숫자를 입력해주세요.")
        return None

    return number


def place_order() -> None:
    print("\n=== 신규 고객 등록 + 상품 주문 ===")

    customer_id = input_positive_int("사용할 고객 ID를 입력하세요: ")
    if customer_id is None:
        return

    customer_name = input("고객 이름을 입력하세요: ").strip()
    customer_phone = input("전화번호를 입력하세요 예) 010-1234-5678: ").strip()
    customer_email = input("이메일을 입력하세요. 선택사항이면 엔터: ").strip()

    if not customer_name:
        print("❌ 고객 이름은 필수입니다.")
        return

    if not customer_phone:
        print("❌ 전화번호는 필수입니다.")
        return

    if not show_products():
        return

    product_id = input_positive_int("\n구매할 상품 ID를 입력하세요: ")
    if product_id is None:
        return

    quantity = input_positive_int("구매할 수량을 입력하세요: ")
    if quantity is None:
        return

    payment_method = input("결제수단을 입력하세요. 기본값 CARD: ").strip().upper()
    if not payment_method:
        payment_method = "CARD"

    try:
        params = {
            "p_customer_id": customer_id,
            "p_customer_name": customer_name,
            "p_email": customer_email if customer_email else None,
            "p_phone": customer_phone,
            "p_product_id": product_id,
            "p_quantity": quantity,
            "p_payment_method": payment_method,
        }

        res = supabase.rpc("place_edu_shopping_order", params).execute()

        if not res.data:
            print("❌ 주문 결과를 받지 못했습니다.")
            return

        result = res.data[0]

        print("\n🎉 주문이 성공적으로 완료되었습니다!")
        print(f"고객명: {customer_name}")
        print(f"주문번호: {result['order_id']}")
        print(f"주문상세번호: {result['order_item_id']}")
        print(f"상품명: {result['product_name']}")
        print(f"수량: {result['quantity']}개")
        print(f"단가: {format_money(result['unit_price'])}")
        print(f"총 결제금액: {format_money(result['total_price'])}")
        print(f"남은 재고: {result['remaining_stock']}개")

        local_order_history.append(
            {
                "order_id": result["order_id"],
                "order_item_id": result["order_item_id"],
                "customer_name": customer_name,
                "product_name": result["product_name"],
                "quantity": result["quantity"],
                "total_price": result["total_price"],
                "remaining_stock": result["remaining_stock"],
            }
        )

    except Exception as e:
        print(f"❌ 주문 처리 실패: {e}")
        print("확인할 것: 고객 ID 중복, 전화번호 중복, 이메일 중복, 상품 ID, 재고 수량, RPC 함수 생성 여부")


def show_local_orders() -> None:
    print("\n=== 현재 실행 세션 주문 내역 ===")

    if not local_order_history:
        print("현재 세션에서 주문한 내역이 없습니다.")
        return

    for idx, order in enumerate(local_order_history, start=1):
        print(
            f"[{idx}] "
            f"주문번호: {order['order_id']} | "
            f"고객명: {order['customer_name']} | "
            f"상품명: {order['product_name']} | "
            f"수량: {order['quantity']}개 | "
            f"금액: {format_money(order['total_price'])} | "
            f"남은 재고: {order['remaining_stock']}개"
        )


def show_recent_db_orders() -> None:
    print("\n=== DB 기준 최근 주문 내역 ===")

    query = """
        order_id,
        order_date,
        order_status,
        payment_method,
        customers(customer_name),
        order_items(
            quantity,
            unit_price,
            discount_rate,
            products(product_name)
        )
    """

    try:
        res = (
            supabase
            .schema("edu_shopping")
            .table("orders")
            .select(query)
            .order("order_id", desc=True)
            .limit(10)
            .execute()
        )

        orders = res.data or []

        if not orders:
            print("DB에 주문 내역이 없습니다.")
            return

        for order in orders:
            customer = order.get("customers") or {}
            items = order.get("order_items") or []

            print("-" * 80)
            print(f"주문번호: {order['order_id']}")
            print(f"고객명: {customer.get('customer_name', '-')}")
            print(f"주문일자: {order['order_date']}")
            print(f"상태: {order['order_status']}")
            print(f"결제수단: {order['payment_method']}")

            for item in items:
                product = item.get("products") or {}

                quantity = item["quantity"]
                unit_price = Decimal(str(item["unit_price"]))
                discount_rate = Decimal(str(item["discount_rate"]))
                total_price = Decimal(quantity) * unit_price * (Decimal("1") - discount_rate)

                print(
                    f"  - 상품명: {product.get('product_name', '-')} | "
                    f"수량: {quantity}개 | "
                    f"금액: {format_money(total_price)}"
                )

    except Exception as e:
        print(f"❌ DB 주문 내역 조회 실패: {e}")
        print("확인할 것: edu_shopping 스키마 Data API 노출 여부, FK 관계, 권한")


def print_menu() -> None:
    print("\n=== 미니 이커머스 시스템 ===")
    print("1. 상품 목록 보기")
    print("2. 상품 주문하기")
    print("3. 현재 세션 주문 내역 보기")
    print("4. DB 최근 주문 내역 보기")
    print("5. 종료")


def main() -> None:
    while True:
        print_menu()
        menu = input("메뉴 선택: ").strip()

        if menu == "1":
            show_products()
        elif menu == "2":
            place_order()
        elif menu == "3":
            show_local_orders()
        elif menu == "4":
            show_recent_db_orders()
        elif menu == "5":
            print("프로그램을 종료합니다.")
            break
        else:
            print("❌ 1~5 중에서 올바른 번호를 선택해주세요.")


if __name__ == "__main__":
    main()