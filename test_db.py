import database as db

def run_tests():
    print("--- 1. Testing DB Initialization ---")
    db.init_db()
    print("OK: DB Initialized.")

    print("\n--- 2. Testing Save Profile ---")
    test_profile = "test_profile_123"
    db.save_loadout_config(test_profile, {
        "must_have": "python, data",
        "or_have": "developer",
        "not_have": "senior",
        "must_include": "remote",
        "must_exclude": "office",
        "country": "Turkey",
        "city": "Istanbul",
        "limit_jobs": 15,
        "delay_seconds": 3.0
    })
    print("OK: Profile Saved.")

    print("\n--- 3. Testing Get Profile ---")
    cfg = db.get_loadout_config(test_profile)
    assert cfg is not None, "Config should not be None"
    assert cfg["must_have"] == "python, data", "must_have mismatch"
    assert cfg["limit_jobs"] == 15, "limit_jobs mismatch"
    print("OK: Profile Loaded correctly:", cfg)

    print("\n--- 4. Testing Get All Profiles ---")
    all_cfgs = db.get_all_loadout_configs()
    assert test_profile in all_cfgs, "test_profile should be in all_configs"
    print("OK: All configs loaded.")

    print("\n--- 5. Testing Delete Profile ---")
    db.delete_loadout(test_profile)
    cfg_after_delete = db.get_loadout_config(test_profile)
    assert cfg_after_delete is None, "Config should be None after deletion"
    print("OK: Profile Deleted.")

if __name__ == "__main__":
    run_tests()
