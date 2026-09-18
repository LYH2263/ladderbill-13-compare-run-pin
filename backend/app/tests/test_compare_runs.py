import pytest

from app import db, seed
from app.repositories import settings as settings_repo
from app.services.billing_service import BillingService


@pytest.fixture()
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with BillingService() as service:
        yield service


def test_pin_snapshot_freezes_factor_and_totals(svc):
    pinned = svc.pin_compare(400)
    assert pinned["peak_factor"] == 1.2
    assert pinned["plain_total"] == 258.00
    assert pinned["peak_total"] == 309.60
    assert pinned["delta"] == 51.60
    assert pinned["deleted_at"] is None
    assert pinned["segments"]["peak_segments"]

    # 全局修改系数：旧钉选详情数字保持不变
    svc.update_settings({"peak_factor": 1.5})
    old = svc.get_compare_run(pinned["id"])
    assert old["peak_factor"] == 1.2
    assert old["peak_total"] == 309.60
    assert old["delta"] == 51.60

    # 新对比使用新系数
    new = svc.pin_compare(400)
    assert new["peak_factor"] == 1.5
    assert new["peak_total"] == 387.00


def test_soft_delete_hidden_from_list_but_detail_readable(svc):
    pinned = svc.pin_compare(400)

    assert svc.delete_compare_run(pinned["id"]) is True
    page = svc.list_compare_runs()
    assert page["total"] == 0
    assert page["items"] == []

    detail = svc.get_compare_run(pinned["id"])
    assert detail is not None
    assert detail["deleted_at"] is not None
    # 完整快照仍可读
    assert detail["peak_factor"] == 1.2
    assert detail["plain_total"] == 258.00
    assert detail["segments"]["plain_segments"]

    # 重复软删返回 False
    assert svc.delete_compare_run(pinned["id"]) is False
    assert svc.get_compare_run(99999) is None


def test_pagination(svc):
    ids = [svc.pin_compare(100 + i)["id"] for i in range(3)]

    first = svc.list_compare_runs(page=1, page_size=2)
    assert first["total"] == 3
    assert [r["id"] for r in first["items"]] == list(reversed(ids))[:2]

    second = svc.list_compare_runs(page=2, page_size=2)
    assert [r["id"] for r in second["items"]] == [ids[0]]


def test_invalid_peak_factor_rejected(svc):
    with pytest.raises(ValueError):
        settings_repo.set_peak_factor(svc._conn, 0)
