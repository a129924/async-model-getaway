# Contract Deviation Rules

Any of the following constitutes a contract deviation, regardless of backward compatibility:

- new parameter not described in the plan (including optional/defaulted parameters)
- removed parameter
- changed parameter type or default value
- changed return type
- new exception raised that the plan does not authorize
- removed exception that the plan keeps
- function or class moved to a different module than the plan specifies
- function or class renamed relative to the plan

The rationale "it has a default value so callers are not broken" does not remove
the deviation. The plan is the authority. If the deviation is intentional and
safe, the plan must be updated and re-approved before the implementation is accepted.
