"""
社團器材借用登記系統 - 組員2：器材借出功能 (borrow_equipment.py)

負責內容：
1. 顯示目前可借的器材清單
2. 器材借出登記（檢查庫存、扣 available、新增借用紀錄）
3. 借出後把動作推入 history_stack，讓組員4的 Stack 復原功能使用
4. 提供 undo_borrow()，讓組員4可以直接呼叫來復原「借出」動作

【資料結構約定】(整合時請跟組員1、3、4 確認一致)

equipment (dict)：器材資料，key 為器材編號
    {
        "E001": {"name": "音響麥克風組", "unit": "組", "total": 3, "available": 3},
        ...
    }

records (list)：借用紀錄，每筆是一個 dict
    {
        "record_id": 1,              # 紀錄編號
        "equipment_id": "E001",
        "borrower": "王小明",
        "quantity": 1,
        "borrow_time": "2026-12-01 14:30:00",
        "return_time": None,         # 尚未歸還為 None
        "status": "借出中",          # "借出中" / "已歸還"
    }

history_stack (list)：操作堆疊 (Stack)，後進先出
    append() 當作 push，pop() 當作 pop
    {"action": "borrow", "record_id": 1, "equipment_id": "E001", "quantity": 1}
"""

from datetime import datetime

STATUS_BORROWED = "借出中"
STATUS_RETURNED = "已歸還"


# ---------------------------------------------------------------
# 工具函式
# ---------------------------------------------------------------
def now_str():
    """回傳目前時間字串，格式：2026-12-01 14:30:00"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def next_record_id(records):
    """產生下一個紀錄編號（目前最大編號 + 1）"""
    if not records:
        return 1
    return max(rec["record_id"] for rec in records) + 1


# ---------------------------------------------------------------
# 顯示可借器材
# ---------------------------------------------------------------
def show_available_equipment(equipment):
    """印出所有器材與目前可借數量"""
    print("\n=== 器材清單 ===")
    print(f"{'編號':<8}{'器材名稱':<14}{'可借/總數'}")
    print("-" * 40)
    for eq_id, item in equipment.items():
        unit = item.get("unit", "")
        print(f"{eq_id:<10}{item['name']:<14}"
              f"{item['available']}/{item['total']}{unit}")


# ---------------------------------------------------------------
# 核心功能：借出器材
# ---------------------------------------------------------------
def borrow_equipment(equipment, records, history_stack,
                     equipment_id, borrower, quantity):
    """
    借出器材。

    參數：
        equipment      器材資料 dict
        records        借用紀錄 list（成功後會新增一筆）
        history_stack  操作堆疊 list（成功後會 push 一筆）
        equipment_id   器材編號
        borrower       借用人姓名
        quantity       借用數量

    回傳：(成功與否: bool, 訊息: str)
    """
    # 1. 檢查借用人
    borrower = borrower.strip()
    if not borrower:
        return False, "借用人姓名不能是空白。"

    # 2. 檢查器材是否存在
    if equipment_id not in equipment:
        return False, f"找不到器材編號 {equipment_id}。"
    item = equipment[equipment_id]
    unit = item.get("unit", "")

    # 3. 檢查數量是否合理
    if not isinstance(quantity, int) or quantity <= 0:
        return False, "借用數量必須是大於 0 的整數。"

    # 4. 檢查庫存是否足夠
    if quantity > item["available"]:
        return False, (f"{item['name']} 目前只剩 {item['available']}{unit}，"
                       f"無法借出 {quantity}{unit}。")

    # 5. 扣掉可用數量、新增借用紀錄
    item["available"] -= quantity
    record = {
        "record_id": next_record_id(records),
        "equipment_id": equipment_id,
        "borrower": borrower,
        "quantity": quantity,
        "borrow_time": now_str(),
        "return_time": None,
        "status": STATUS_BORROWED,
    }
    records.append(record)

    # 6. 推入 Stack，給組員4的復原功能使用
    history_stack.append({
        "action": "borrow",
        "record_id": record["record_id"],
        "equipment_id": equipment_id,
        "quantity": quantity,
    })

    return True, (f"借出成功（紀錄 {record['record_id']}）：{borrower} 借 "
                  f"{item['name']} {quantity}{unit}"
                  f"（剩餘 {item['available']}/{item['total']}{unit}）")


# ---------------------------------------------------------------
# 復原「借出」動作（提供給組員4整合：pop 到 action == "borrow" 時呼叫）
# ---------------------------------------------------------------
def undo_borrow(equipment, records, action):
    """
    復原一筆借出動作：把可用數量加回去，並刪除那筆借用紀錄。
    action 就是 borrow_equipment() 推入 Stack 的那個 dict。

    回傳：(成功與否: bool, 訊息: str)
    """
    target = None
    for rec in records:
        if rec["record_id"] == action["record_id"]:
            target = rec
            break
    if target is None:
        return False, "復原失敗：找不到對應的借用紀錄。"
    if target["status"] != STATUS_BORROWED:
        return False, "復原失敗：該器材已經歸還，請先復原歸還動作。"

    item = equipment.get(action["equipment_id"])
    if item is None:
        return False, "復原失敗：找不到對應的器材。"

    item["available"] += action["quantity"]
    records.remove(target)
    return True, f"已復原借出：紀錄 {action['record_id']} 已取消。"


# ---------------------------------------------------------------
# 借出功能的操作介面（讓主程式選單直接呼叫這個）
# ---------------------------------------------------------------
def borrow_menu(equipment, records, history_stack):
    """互動式借出流程：顯示器材 → 輸入編號、姓名、數量 → 借出"""
    show_available_equipment(equipment)

    equipment_id = input("\n請輸入器材編號（例如 E001，輸入 0 取消）：").strip().upper()
    if equipment_id == "0":
        print("已取消借出。")
        return

    borrower = input("請輸入借用人姓名：").strip()

    text = input("請輸入借用數量：").strip()
    if not text.isdigit():
        print("✘ 數量請輸入數字。")
        return

    ok, msg = borrow_equipment(equipment, records, history_stack,
                               equipment_id, borrower, int(text))
    print(("✔ " if ok else "✘ ") + msg)


# ---------------------------------------------------------------
# 單獨測試用：python borrow_equipment.py
# 整合到主程式後，這一段不會被執行
# ---------------------------------------------------------------
if __name__ == "__main__":
    # 假資料（整合時會換成組員1提供的真實資料）
    equipment = {
        "E001": {"name": "音響麥克風組", "unit": "組", "total": 3, "available": 3},
        "E002": {"name": "手提式擴音機", "unit": "台", "total": 3, "available": 3},
        "E003": {"name": "單槍投影機", "unit": "台", "total": 2, "available": 2},
        "E004": {"name": "移動式投影布幕", "unit": "組", "total": 2, "available": 2},
        "E005": {"name": "折疊長桌", "unit": "張", "total": 10, "available": 10},
        "E006": {"name": "塑膠椅", "unit": "張", "total": 40, "available": 40},
        "E007": {"name": "動力延長線", "unit": "捲", "total": 4, "available": 4},
        "E008": {"name": "手推車", "unit": "台", "total": 3, "available": 3},
    }
    records = []
    history_stack = []

    while True:
        print("\n--- 借出功能測試 ---")
        print("1. 借出器材")
        print("2. 查看器材清單")
        print("3. 復原上一個借出動作（測試 undo_borrow）")
        print("0. 離開")
        choice = input("請選擇：").strip()

        if choice == "1":
            borrow_menu(equipment, records, history_stack)
        elif choice == "2":
            show_available_equipment(equipment)
        elif choice == "3":
            if history_stack and history_stack[-1]["action"] == "borrow":
                ok, msg = undo_borrow(equipment, records, history_stack.pop())
                print(("✔ " if ok else "✘ ") + msg)
            else:
                print("沒有可復原的借出動作。")
        elif choice == "0":
            break
        else:
            print("無效的選項。")
