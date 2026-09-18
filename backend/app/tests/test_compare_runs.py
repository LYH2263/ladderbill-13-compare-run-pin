"""钉选快照、软删除与分页的集成测试。

通过 DATA_DIR 环境变量把数据库指向临时目录，须在导入 app.config 之前设置。
"""

import json
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="ladderbill-test-")
os.environ["DATA_DIR"] = _tmp

from app import seed  # noqa: E402
from app.services.billing_service import BillingService  # noqa: E402


def setup_function(_):
    # 每个用例一个全新数据库
    db_path = os.path.join(_tmp, "app.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    seed.init_db()


def _result(run):
    return json.loads(run["result_json"])


def _payload(run):
    return json.loads(run["input_json"])


def test_compare_persists_peak_factor_snapshot():
    with BillingService() as svc:
        r = svc.run_compare(400, persist=True)
        detail = svc.get_run(r["run_id"])
    assert _payload(detail)["peak_factor"] == 1.2
    assert _result(detail)["peak_factor"] == 1.2
    assert _result(detail)["plain_total"] == 258.00
    assert _result(detail)["peak_total"] == 309.60
    assert _result(detail)["delta"] == 51.60


def test_pinned_snapshot_survives_settings_change():
    with BillingService() as svc:
        first = svc.run_compare(400, persist=True, pinned=True)
        pinned_id = first["run_id"]
        pinned_before = svc.get_run(pinned_id)

        # 全局修改系数
        svc.update_peak_factor(1.5)

        pinned_after = svc.get_run(pinned_id)
        # 旧钉选：系数与合计数字保持钉选当时的值
        assert _payload(pinned_after)["peak_factor"] == 1.2
        assert _result(pinned_after)["peak_factor"] == 1.2
        assert _result(pinned_after)["peak_total"] == 309.60
        assert _result(pinned_after)["delta"] == 51.60
        assert pinned_after["pinned"] is True
        assert pinned_after["result_json"] == pinned_before["result_json"]

        # 新对比使用新系数
        second = svc.run_compare(400, persist=True)
        assert second["peak_factor"] == 1.5
        assert second["peak_total"] == 387.00  # 258 * 1.5


def test_pin_existing_run_then_change_factor():
    with BillingService() as svc:
        r = svc.run_compare(400, persist=True)
        rid = r["run_id"]
        svc.pin_compare_run(rid, True)
        svc.update_peak_factor(1.8)
        detail = svc.get_run(rid)
    assert _payload(detail)["peak_factor"] == 1.2
    assert _result(detail)["peak_total"] == 309.60
    assert detail["pinned"] is True
    assert detail["pinned_at"]


def test_soft_delete_hidden_from_list_but_detail_readable():
    with BillingService() as svc:
        r = svc.run_compare(400, persist=True)
        rid = r["run_id"]
        svc.delete_compare_run(rid)

        page = svc.list_compare_runs()
        assert all(it["id"] != rid for it in page["items"])

        detail = svc.get_run(rid)
        assert detail is not None
        assert detail["deleted_at"]
        # 完整快照仍可读
        assert _result(detail)["peak_total"] == 309.60


def test_pagination_and_pin_ordering():
    with BillingService() as svc:
        ids = [svc.run_compare(100 + i, persist=True)["run_id"] for i in range(5)]
        svc.pin_compare_run(ids[1], True)

        page1 = svc.list_compare_runs(page=1, page_size=3)
        # 含种子库自带的 1 条 compare，共 6 条
        assert page1["total"] == 6
        assert len(page1["items"]) == 3
        # 钉选项排在首页最前
        assert page1["items"][0]["id"] == ids[1]
        assert page1["items"][0]["pinned"] is True

        page2 = svc.list_compare_runs(page=2, page_size=3)
        assert len(page2["items"]) == 3
        page_ids = {it["id"] for it in page1["items"]} | {it["id"] for it in page2["items"]}
        assert len(page_ids) == 6


def test_pin_and_unpin_toggles():
    with BillingService() as svc:
        rid = svc.run_compare(400, persist=True)["run_id"]
        pinned = svc.pin_compare_run(rid, True)
        assert pinned["pinned"] is True
        unpinned = svc.pin_compare_run(rid, False)
        assert unpinned["pinned"] is False
        assert unpinned["pinned_at"] is None


def test_compare_run_endpoints_reject_non_compare_kind():
    with BillingService() as svc:
        # 种子库自带一条 bill 记录（id 可能为 1），钉选/删除只针对 compare
        bill_run = svc.run_bill(100, peak=False, account_id=None, persist=True)
        assert svc.pin_compare_run(bill_run["run_id"], True) is None
        assert svc.delete_compare_run(bill_run["run_id"]) is None
