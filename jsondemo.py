import json

l = []

l.append(1)
l.append(0)
l.append(0)
l.append(0)
l.append(0)
l.append(1)
l.append(1)
l.append(1)
l.append(1)
l.append(1)
l.append(1)

print(l)
print(type(l))

print(json.dumps(l))
print(type(json.dumps(l)))

m = {
    "status": 0,
    "data": type(json.dumps(l)),
}
j = json.dumps(m)
print(j)
