from datetime import datetime, timezone

print(timezone)
dls = []
dls.append(datetime(2024,6,1,22))
dls.append(datetime(2024,6,2,4))
dls.append(datetime(2024,6,2,10))
dls.append(datetime(2024,6,2,12,10))

print(dls[3].hour)
