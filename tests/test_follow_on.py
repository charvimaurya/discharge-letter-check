"""follow_on: kept only when the letter states it word for word, with its minutes, after a real task."""

from discharge_letter_check import FollowOn, RecoveryState, Source, Task, validate_recovery_plan


EXERCISES = "Do your knee exercises 3 times a day."
WALK = "Walk for 5 to 10 minutes, 4 times a day."
ICE = "Ice pack on the knee for 20 minutes after each set of exercises."
LETTER = f"DAILY ACTIVITIES\n{EXERCISES}\n{WALK}\n{ICE}\nRest with your leg raised between activities.\n"


def _plan(follow_on, letter=LETTER):
    state = RecoveryState("p", "d", tasks=[
        Task("ex", EXERCISES, kind="exercise", source=Source("d", EXERCISES, page=1)),
        Task("walk", WALK, kind="walk", source=Source("d", WALK, page=1)),
        Task("ice", ICE, kind="care", source=Source("d", ICE, page=1), follow_on=follow_on),
    ])
    return validate_recovery_plan(state, document_text=letter)


def _good(**changes):
    values = {"after_task_id": "ex", "duration_minutes": 20, "source": Source("d", ICE, page=1)}
    return FollowOn(**{**values, **changes})


def _ice(state):
    return next(task for task in state.tasks if task.id == "ice")


def test_follow_on_stated_in_the_letter_is_kept():
    follow_on = _ice(_plan(_good())).follow_on

    assert follow_on.after_task_id == "ex"
    assert follow_on.duration_minutes == 20
    assert follow_on.source.snippet == ICE


def test_snippet_not_in_the_letter_is_dropped():
    reworded = Source("d", "Use an ice pack for 20 minutes after exercising.", page=1)

    assert _ice(_plan(_good(source=reworded))).follow_on is None


def test_minutes_not_in_the_snippet_are_dropped():
    assert _ice(_plan(_good(duration_minutes=30))).follow_on is None


def test_missing_minutes_are_dropped():
    assert _ice(_plan(_good(duration_minutes=None))).follow_on is None


def test_missing_source_is_dropped():
    assert _ice(_plan(_good(source=None))).follow_on is None


def test_follow_on_pointing_at_no_task_is_dropped():
    assert _ice(_plan(_good(after_task_id="swim"))).follow_on is None


def test_follow_on_pointing_at_its_own_task_is_dropped():
    assert _ice(_plan(_good(after_task_id="ice"))).follow_on is None


def test_no_follow_on_when_the_letter_gives_none():
    assert _ice(_plan(None)).follow_on is None


def test_without_the_letter_text_the_snippet_is_not_checked_against_it():
    assert _ice(_plan(_good(), letter=None)).follow_on is not None
