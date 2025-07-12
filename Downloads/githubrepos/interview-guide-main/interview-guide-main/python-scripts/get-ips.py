import re
values = []
with open('input.txt', 'r') as file:
    for l in file:
        data = re.search(r'([0-9]{1,3}\.){3}[0-9]{1,3}', l)
        if data:
            values.append(data.group(0))
for i in values:
    print(i)


---

With (...) (capturing group), findall returns only the last captured group
With (?:...) (non-capturing group), findall returns the complete matches

import re
with open('input.txt', 'r') as file:
  for l in file:

        data = re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', l)
        print(data)
