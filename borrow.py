# borrow.py — 器材借出功能(組員2)
#
# 共用的 state 結構(與組員1、3、4、5 約定):
#   state = {
#       "equipment": {"E001": {"name": "籃球", "total": 10, "available": 10}},
#       "loans": {"L001": {"loan_id": "L001", "equipment_id": "E001",
#                          "borrower": "王小明", "quantity": 2, "status": "借出"}},
#       "history": [],
#       "undo_stack": [],
#   }

try:
    from history import save_snapshot, record_action
except ImportError:  # 組員4的檔案還沒放進來時,先用空函式讓本檔可以單獨測試
    def save_snapshot(state):
        pass

    def record_action(state, action, details):
        pass


def generate_loan_id(state):
    """產生不重複的借用單號,例如 L001、L002。"""
    max_num = 0
    for loan_id in state["loans"]:
        if loan_id.startswith("L") and loan_id[1:].isdigit():
            max_num = max(max_num, int(loan_id[1:]))
    return f"L{max_num + 1:03d}"


def borrow_equipment(state, item_id, borrower, quantity):
    """
    借出器材。
    成功:回傳 (True, "借出成功,借用單號:L001")
    失敗:回傳 (False, "錯誤原因")
    """
    item_id = str(item_id).strip()
    borrower = str(borrower).strip()

    # 1. 檢查借用人
    if not borrower:
        return False, "借用人姓名不可空白"

    # 2. 檢查器材是否存在
    if item_id not in state["equipment"]:
        return False, f"查無器材編號:{item_id}"

    # 3. 檢查數量是否為正整數
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return False, "借用數量必須是整數"
    if quantity <= 0:
        return False, "借用數量必須大於 0"

    # 4. 檢查可借數量
    item = state["equipment"][item_id]
    if quantity > item["available"]:
        return False, f"可借數量不足:{item['name']} 目前剩 {item['available']} 件"

    # 5. 通過檢查後,先存快照(供撤銷),再修改資料
    save_snapshot(state)

    loan_id = generate_loan_id(state)
    item["available"] -= quantity
    state["loans"][loan_id] = {
        "loan_id": loan_id,
        "equipment_id": item_id,
        "borrower": borrower,
        "quantity": quantity,
        "status": "借出",
    }

    # 6. 記錄歷程
    record_action(state, "借出", {
        "loan_id": loan_id,
        "equipment_id": item_id,
        "borrower": borrower,
        "quantity": quantity,
    })

    return True, f"借出成功,借用單號:{loan_id}"


if __name__ == "__main__":
    # 簡單測試
    state = {
        "equipment": {"E001": {"name": "籃球", "total": 10, "available": 10}},
        "loans": {},
        "history": [],
        "undo_stack": [],
    }
    print(borrow_equipment(state, "E001", "王小明", 2))   # 成功
    print(borrow_equipment(state, "E001", "李小華", 20))  # 數量不足
    print(borrow_equipment(state, "E001", "", 1))         # 借用人空白
    print(borrow_equipment(state, "E999", "陳大文", 1))   # 查無器材
    print(borrow_equipment(state, "E001", "陳大文", -1))  # 數量錯誤
    print(state["equipment"], state["loans"])

