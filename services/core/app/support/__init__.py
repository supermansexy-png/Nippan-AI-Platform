"""Support agent change path (T-079e).

An existing customer asks in chat to change their business info. The
Support agent applies the change **within fixed menus only** and flags
anything that could raise cost to Cost Guard **first**.

Reuse, never rebuild: config parsing/driving comes from
``app/onboarding/`` (menus, ConfigDraft, signals); the status transition
goes ONLY through ``app/onboarding/gate.py`` (the one path to ``active``, and
``edit``/decline revoke to ``paused``). There is no second way to write a
config row or to set ``status`` here.
"""
