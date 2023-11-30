import renpy
"""renpy
init python:
"""

# make a decorator version ? meh, not picklable...
def a_wait_list(func, *args, restart_interaction=True, **kwargs):
    """
    Takes a callable function which returns a list but takes time.
    Returns immediately an empty list and schedules the function to populate it.
    When the "populator" function returns, side-effects it to the previously returned list,
    and restarts the interaction (for a use in screens).
    """
    rv = []

    def threaded():
        """
        Calls the function, collects the return value,
        lodges the side-effect update in the main thread.
        """
        late_rv = func(*args, **kwargs)

        renpy.invoke_in_main_thread(rv.extend, late_rv)
        if restart_interaction:
            renpy.invoke_in_main_thread(renpy.restart_interaction)

    renpy.invoke_in_thread(threaded)
    return rv

def a_wait_dict(func, *args, restart_interaction=True, **kwargs):
    rv = {}
    def threaded():
        late_rv = func(*args, **kwargs)
        renpy.invoke_in_main_thread(rv.update, late_rv)
        if restart_interaction:
            renpy.invoke_in_main_thread(renpy.restart_interaction)
    renpy.invoke_in_thread(threaded)
    return rv
