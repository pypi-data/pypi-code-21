import os


class TestExAppOptions:

    allowed_users = os.path.join(os.path.dirname(__file__), "users.txt")

    competitions = [dict(cpt_id=0,
                         name="compet1",
                         link="http://...",
                         expected_values=os.path.join(os.path.dirname(
                             __file__), "off_eval_all_Y.txt"),
                         description="desc",
                         metric="mean_squared_error")]
