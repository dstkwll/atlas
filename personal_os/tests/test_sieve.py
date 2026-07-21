from personal_os.poller.sieve import is_noise

RULES = {
    "sender_patterns": ["no-reply@", "newsletter@", "@promotions."],
    "subject_patterns": ["unsubscribe", "% off"],
    "list_unsubscribe_header": True,
}


def test_drops_noreply_sender():
    drop, why = is_noise(
        {"from": "no-reply@bank.com", "subject": "Statement", "headers": {}}, RULES
    )
    assert drop and "sender" in why


def test_unknown_sender_survives_fail_open():
    drop, why = is_noise(
        {"from": "aunt.sue@gmail.com", "subject": "Malcolm bday", "headers": {}}, RULES
    )
    assert drop is False
    assert why == ""


def test_subject_pattern_dropped():
    drop, why = is_noise(
        {"from": "store@x.com", "subject": "50% off sale", "headers": {}}, RULES
    )
    assert drop and "subject" in why


def test_list_unsubscribe_header_dropped():
    drop, why = is_noise(
        {"from": "x@store.com", "subject": "hi", "headers": {"List-Unsubscribe": "<...>"}},
        RULES,
    )
    assert drop and "list-unsubscribe" in why


def test_case_insensitive_sender():
    drop, _ = is_noise(
        {"from": "No-Reply@Bank.com", "subject": "x", "headers": {}}, RULES
    )
    assert drop


def test_empty_rules_everything_survives():
    drop, _ = is_noise(
        {"from": "no-reply@bank.com", "subject": "unsubscribe", "headers": {}}, {}
    )
    assert drop is False
