import bot


def test__check_args__given__2__args__expect__2__args__should__return__true():
    args = "a b c"
    expected_args = [str, str]
    expected_result = True
    result = bot._check_args(args, expected_args)
    assert result == expected_result


def test__check_args__given__2__args__expected__3__args__should__return__false():
    args = "a b c"
    expected_args = [str, str, str]
    expected_result = False
    result = bot._check_args(args, expected_args)
    assert result == expected_result
