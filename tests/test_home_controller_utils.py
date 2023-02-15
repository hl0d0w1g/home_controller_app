"""
Testing the home_controller.utils module.
"""

# import datetime
# import pytest

# from home_controller.utils import time_str_to_time, get_datetime


class TestHomeControllerUtils:
    """
    Test functions of home_controller.utils module.
    """
    def test_sample(self) -> None:
        '''test'''
        assert True

#     @pytest.mark.parametrize(
#         'in_value, expected',
#         [
#             ('20:00', datetime.time.fromisoformat('20:00')),
#             ('00:00', datetime.time.fromisoformat('00:00')),
#         ],
#     )
#     def test_time_str_to_time(self, in_value, expected):
#         """
#         Test the time_str_to_time function.
#         """
#         assert time_str_to_time(in_value) == expected

#     def test_current_datetime(self):
#         """
#         Test the current_datetime function.
#         """
#         assert isinstance(get_datetime(), datetime.datetime)
