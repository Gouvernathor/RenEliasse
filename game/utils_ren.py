import renpy # type: ignore
python_object = object

"""renpy
init python:
"""

__notpassed = python_object()

def a_wait_list(func, *, default_rv=__notpassed, error_rv, restart_interaction=True):
    """
    Takes a callable function which returns a list but takes time.
    Returns immediately an empty list and schedules the function to populate it.
    When the "populator" function returns, side-effects it to the previously returned list,
    and restarts the interaction (for a use in screens).

    default_rv and error_rv should be iterables.
    """

    if default_rv is __notpassed:
        rv = []
    else:
        rv = list(default_rv)

    def threaded():
        """
        Calls the function, collects the return value,
        lodges the side-effect update in the main thread.
        """

        try:
            late_rv = func()
        except Exception:
            late_rv = error_rv

        def unthreaded():
            rv[:] = late_rv

            if restart_interaction:
                renpy.restart_interaction()

        renpy.invoke_in_main_thread(unthreaded)

    renpy.invoke_in_thread(threaded)
    return rv

def a_wait_dict(func, *, default_rv=__notpassed, error_rv, restart_interaction=True):
    if default_rv is __notpassed:
        rv = {}
    else:
        rv = dict(default_rv)

    def threaded():
        try:
            late_rv = func()
        except Exception:
            late_rv = error_rv

        def unthreaded():
            rv.clear()
            rv.update(late_rv)

            if restart_interaction:
                renpy.restart_interaction()

        renpy.invoke_in_main_thread(unthreaded)

    renpy.invoke_in_thread(threaded)
    return rv
