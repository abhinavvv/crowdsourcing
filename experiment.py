import pickle
from collections import Counter
import codecs
from collections import OrderedDict

with open('r_lsi.pik', 'rb') as pk:
    r_lsi = pickle.load(pk)


with open('r_bow.pik', 'rb') as pk:
    r_bow = pickle.load(pk)


with open('a.pik', 'rb') as pk:
    a = pickle.load(pk)
#
c = Counter(a)
# c = c.most_common()
print c
# print(r_lsi)
#
# for elem in c:
#     user, count = elem
#     user_x = user.encode('ascii', 'ignore')
#     print 'User :{}  Counter :{}  Reputation_by_topics:{}  Reputation_by_bow={}'\
#         .format(user_x, count, r_lsi[user], r_bow[user])
#

r_lsi_sorted = OrderedDict(sorted(r_lsi.items(), key=lambda x: -x[1]))
r_bow_sorted = OrderedDict(sorted(r_bow.items(), key=lambda x: -x[1]))

print(r_lsi_sorted)
print(r_bow_sorted)

r_lsi_list = []
r_bow_list = []

for user, reputation in r_lsi_sorted.iteritems():
    elem = (user, reputation, c[user])
    r_lsi_list.append(elem)
print r_lsi_list

for user, reputation in r_bow_sorted.iteritems():
    elem = (user, reputation, c[user])
    r_bow_list.append(elem)
print r_bow_list

with open('r_lsi_list', 'wb') as pk:
    pickle.dump(r_lsi_list, pk)

with open('r_bow_list', 'wb') as pk:
    pickle.dump(r_bow_list, pk)

