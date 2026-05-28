import random
from datetime import datetime
from getpass import getpass
from supabase import create_client

# 전역 변수로 관리할 로컬 주문 캐시
local_order_history = []


def connect_supabase():
    url = input("Supabase URL: ").strip()
    anon_key = getpass("Supabase anon key: ").strip()

    client = create_client(url, anon_key)
    print("Supabase 연결 완료")
    return client


# Supabase 연결 초기화
supabase = connect_supabase()


def show_products():
    print("\n=== 판매 중인 상품 목록 (재고 포함) ===")
    try:
        # 💡 .schema("edu_shopping")를 명시하여 직접 커스텀 스키마를 조회합니다.
        res = (
            supabase
            .schema("edu_shopping")
            .table("products")
            .select("product_id, product_name, list_price, status, inventory(quantity)")
            .eq("status", "정상")
            .execute()
        )
        
        products = res.data

        if not products:
            print("현재 등록된 상품이 없습니다.")
            return False

        print(f"{'ID':<5} | {'상품명':<22} | {'가격':<10} | {'재고량':<6} | {'상태':<5}")
        print("-" * 65)
        
        for p in products:
            inv_data = p.get("inventory")
            stock = inv_data["quantity"] if inv_data else 0
            
            print(
                f"{p['product_id']:<5} | {p['product_name']:<20} | {p['list_price']:<10} | {stock:<6} | {p['status']:<5}"
            )
        return True

    except Exception as e:
        print(f"상품 목록을 불러오는 중 오류 발생: {e}")
        return False


def place_order():
    print("\n=== 신규 고객 정보 및 주문 등록 ===")

    # 1. 고객 ID 중복 검사 및 입력 루프 (edu_shopping 스키마 기준)
    while True:
        customer_id_input = input("사용할 고객 ID를 입력하세요 (숫자): ").strip()
        if not customer_id_input.isdigit():
            print("❌ 올바른 숫자로만 입력해주세요.")
            continue
        
        customer_id = int(customer_id_input)
        
        try:
            # 💡 중복 체크 시에도 edu_shopping 스키마 지정
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

    current_date = datetime.now().strftime("%Y-%m-%d")

    # 상품 목록 보여주기 (재고 포함)
    if not show_products():
        return

    # 3. 주문 상품 정보 입력 받기
    product_id_input = input("\n구매할 상품 ID를 입력하세요: ").strip()
    quantity_input = input("구매할 수량을 입력하세요: ").strip()

    if not (product_id_input.isdigit() and quantity_input.isdigit()):
        print("❌ 오류: 상품 ID와 수량은 숫자로만 입력해야 합니다.")
        return

    p_id = int(product_id_input)
    qty = int(quantity_input)

    try:
        # [단계 1] 선택한 상품의 가격 및 재고 조회 (edu_shopping 스키마 지정)
        p_res = (
            supabase
            .schema("edu_shopping")
            .table("products")
            .select("list_price, product_name, inventory(quantity)")
            .eq("product_id", p_id)
            .single()
            .execute()
        )
        product_data = p_res.data

        if not product_data:
            print("❌ 오류: 존재하지 않는 상품 ID입니다.")
            return

        unit_price = product_data["list_price"]
        product_name = product_data["product_name"]
        
        inv_data = product_data.get("inventory")
        current_stock = inv_data["quantity"] if inv_data else 0

        # 재고 부족 검증
        if current_stock < qty:
            print(f"❌ 주문 실패: 재고가 부족합니다. (현재 재고: {current_stock}개)")
            return

        # [단계 2] customers 테이블에 신규 고객 정보 삽입
        customer_record = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "email": customer_email if customer_email else None,
            "phone": customer_phone,
            "signup_date": current_date
        }
        
        print("\n고객 정보 등록 중...")
        supabase.schema("edu_shopping").table("customers").insert(customer_record).execute()

        # [단계 3] orders 테이블에 주문 마스터 생성
        order_id = random.randint(100000, 999999)
        order_record = {
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": current_date,
            "order_status": "PAID",
            "payment_method": "CARD",
        }

        # [단계 4] order_items 테이블에 주문 상세 내역 생성
        order_item_id = random.randint(100000, 999999)
        discount_rate = 0.0

        item_record = {
            "order_item_id": order_item_id,
            "order_id": order_id,
            "product_id": p_id,
            "quantity": qty,
            "unit_price": unit_price,
            "discount_rate": discount_rate,
        }

        # Supabase DB에 주문 정보 최종 저장 (모두 edu_shopping 스키마 지정)
        supabase.schema("edu_shopping").table("orders").insert(order_record).execute()
        supabase.schema("edu_shopping").table("order_items").insert(item_record).execute()

        # [단계 5] 재고(inventory) 차감
        new_stock = current_stock - qty
        supabase.schema("edu_shopping").table("inventory").update({"quantity": new_stock}).eq("product_id", p_id).execute()

        total_price = qty * unit_price * (1 - discount_rate)
        print(f"\n🎉 {customer_name} 회원님의 주문이 성공적으로 완료되었습니다!")
        print(f"주문 상품: {product_name} / 수량: {qty}개 / 남은 재고: {new_stock}개 / 총 결제금액: {int(total_price)}원")

        # 로컬 캐시에 기록 저장
        local_order_history.append(
            {
                "order_id": order_id,
                "product_name": product_name,
                "quantity": qty,
                "total_price": total_price,
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
        print(
            f"[{idx}] 주문번호: {ord['order_id']} | 상품명: {ord['product_name']} | 수량: {ord['quantity']}개 | 금액: {int(ord['total_price'])}원"
        )


def print_menu():
    print("\n=== 미니 이커머스 시스템 ===")
    print("1. 상품 목록 보기 (재고 포함)")
    print("2. 상품 주문하기 (신규 회원 등록 포함)")
    print("3. 최근 주문 내역 보기 (로컬 캐시)")
    print("4. 종료")


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
            print("프로그램을 종료합니다.")
            break
        else:
            print("1~4 중에서 올바른 번호를 선택해주세요.")


if __name__ == "__main__":
    main()