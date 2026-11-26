"""equipment.py - 器材資料管理（使用 Dictionary）

state 的結構：以「器材編號」為 key，內層 Dictionary 存放該器材資料。
    {
        "E001": {"name": "音響麥克風組", "quantity": 3, "available": 3, "unit": "組"},
        ...
    }
"""

import unicodedata

MAX_QUANTITY = 10000  # 單筆器材數量上限，超過視為不合理

# 預設器材資料：(編號, 名稱, 數量, 單位)
SAMPLE_EQUIPMENT = [
    ("E001", "音響麥克風組", 3, "組"),
    ("E002", "手提式擴音機", 3, "台"),
    ("E003", "單槍投影機", 2, "台"),
    ("E004", "移動式投影布幕", 2, "組"),
    ("E005", "折疊長桌", 10, "張"),
    ("E006", "塑膠椅", 40, "張"),
    ("E007", "動力延長線", 3, "卷"),
    ("E008", "手推車", 3, "台"),
]


def add_equipment(state, item_id, name, quantity, unit=""):
    """新增器材。unit 為選填的單位（組、台、張…），不影響原本三個必填參數。

    成功回傳 (True, 訊息)；失敗回傳 (False, 錯誤原因)，且不會修改 state。
    """
    # 檢查器材編號
    if not isinstance(item_id, str) or not item_id.strip():
        return False, "器材編號不可為空白。"
    item_id = item_id.strip()

    # 檢查名稱
    if not isinstance(name, str) or not name.strip():
        return False, "器材名稱不可為空白。"
    name = name.strip()

    # 檢查數量：必須是整數（bool 也是 int 的子類別，需排除）
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return False, "數量必須是整數。"
    if quantity < 0:
        return False, "數量不可為負數。"
    if quantity == 0:
        return False, "數量必須大於 0。"
    if quantity > MAX_QUANTITY:
        return False, f"數量不合理，單筆上限為 {MAX_QUANTITY}。"

    # 防止重複編號
    if item_id in state:
        return False, f"器材編號 {item_id} 已存在，無法重複新增。"

    state[item_id] = {
        "name": name,
        "quantity": quantity,   # 總數量
        "available": quantity,  # 目前可借數量（剛新增時等於總數量）
        "unit": unit.strip() if isinstance(unit, str) else "",
    }
    return True, f"已新增器材：{item_id} {name}，數量 {quantity}{state[item_id]['unit']}。"


def load_sample_data(state):
    """把 SAMPLE_EQUIPMENT 載入 state（同樣經過 add_equipment 驗證）。"""
    for item_id, name, quantity, unit in SAMPLE_EQUIPMENT:
        add_equipment(state, item_id, name, quantity, unit)
    return state


def _pad(text, width):
    """依顯示寬度補空白（中文字佔 2 格），讓表格對齊。"""
    w = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
    return text + " " * max(width - w, 0)


def list_equipment(state):
    """顯示所有器材及目前可借數量，並回傳器材清單（list of tuple）。"""
    if not state:
        print("目前沒有任何器材資料。")
        return []

    print(_pad("編號", 8) + _pad("名稱", 18) + "可借數量")
    print("-" * 38)
    rows = []
    for item_id, info in state.items():
        unit = info.get("unit", "")
        print(_pad(item_id, 8) + _pad(info["name"], 18)
              + f"{info['available']}/{info['quantity']}{unit}")
        rows.append((item_id, info["name"], info["available"], info["quantity"]))
    return rows


def get_equipment(state, item_id):
    """用器材編號查詢指定器材。

    找到時回傳該器材資料（Dictionary 的複本，避免外部誤改）；
    找不到時回傳 None。
    """
    if not isinstance(item_id, str):
        return None
    info = state.get(item_id.strip())
    if info is None:
        return None
    return {"id": item_id.strip(), **info}


# ---------------------------------------------------------------------------
# 簡易文字選單（供手動測試）
# ---------------------------------------------------------------------------
def main():
    state = {}
    load_sample_data(state)  # 啟動時先載入預設器材
    while True:
        print("\n=== 器材管理 ===")
        print("1. 新增器材")
        print("2. 顯示所有器材")
        print("3. 查詢器材")
        print("0. 離開")
        choice = input("請選擇：").strip()

        if choice == "1":
            item_id = input("器材編號：")
            name = input("器材名稱：")
            raw = input("數量：").strip()
            unit = input("單位（可留空）：")
            try:
                quantity = int(raw)
            except ValueError:
                print("數量必須是整數。")
                continue
            ok, msg = add_equipment(state, item_id, name, quantity, unit)
            print(msg)
        elif choice == "2":
            list_equipment(state)
        elif choice == "3":
            item_id = input("請輸入器材編號：")
            item = get_equipment(state, item_id)
            if item is None:
                print("查無此器材。")
            else:
                print(f"編號：{item['id']}  名稱：{item['name']}  "
                      f"可借數量：{item['available']}/{item['quantity']}{item['unit']}")
        elif choice == "0":
            print("結束程式。")
            break
        else:
            print("無效的選項，請重新輸入。")


if __name__ == "__main__":
    main()
