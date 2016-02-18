# demo_counter.py
# inputs
#  name   - counter name token string
#  enable - bool to enable counting
#  reset  - bool to reset to lowest value
#  low    - lowest output value
#  high   - upper bound on output value
#  step   - interval to step

# outputs
#   value - integer count value

import scriptcontext as sc

value = sc.sticky.get(name)

if value is None or reset or value >= high:
    value = low

elif enable:
    value = value + step

sc.sticky[name] = value
print value