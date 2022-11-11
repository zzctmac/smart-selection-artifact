import ctypes
import pandas as pd
from multiprocessing import Value, Queue
from multiprocessing import Process

k = Value(ctypes.py_object)
q = Queue()


def f(eq):
    df = pd.DataFrame({'a': range(0, 9),
                       'b': range(10, 19),
                       'c': range(100, 109)})
    eq.put(('a', df))


ps = []
for i in range(0, 2):
    p = Process(target=f, args=(q,))
    p.start()
    ps.append(p)

print(q.get())

print("----")
print(q.get())

print(q.get())

for p in ps:
    p.join()
